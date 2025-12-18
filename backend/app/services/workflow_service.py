"""Workflow automation engine"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Workflow, WorkflowRun, Message, Conversation
from app.services.ai_service import ai_service


class WorkflowEngine:
    """Engine for executing automation workflows"""
    
    def __init__(self):
        self.node_handlers = {
            "condition": self._handle_condition,
            "action": self._handle_action,
            "delay": self._handle_delay,
            "ai_response": self._handle_ai_response,
            "send_message": self._handle_send_message,
            "update_tag": self._handle_update_tag,
            "create_order": self._handle_create_order,
        }
    
    async def execute_workflow(
        self,
        workflow: Workflow,
        trigger_data: Dict[str, Any],
        db: AsyncSession
    ) -> WorkflowRun:
        """Execute a workflow with given trigger data"""
        # Create run record
        run = WorkflowRun(
            workflow_id=workflow.id,
            status="in_progress",
            trigger_data=trigger_data,
            execution_log=[],
            started_at=datetime.utcnow()
        )
        db.add(run)
        await db.commit()
        
        try:
            # Find start node (first node or node without incoming connections)
            nodes = workflow.nodes or []
            connections = workflow.connections or []
            
            if not nodes:
                run.status = "completed"
                run.completed_at = datetime.utcnow()
                await db.commit()
                return run
            
            # Build connection map
            incoming = {conn["target_id"]: conn["source_id"] for conn in connections}
            start_nodes = [n for n in nodes if n["id"] not in incoming]
            
            if not start_nodes:
                start_nodes = [nodes[0]]
            
            # Execute from start nodes
            context = {"trigger_data": trigger_data, "variables": {}}
            
            for start_node in start_nodes:
                await self._execute_node(start_node, nodes, connections, context, run, db)
            
            run.status = "completed"
            run.completed_at = datetime.utcnow()
            
        except Exception as e:
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
        
        # Update workflow stats
        workflow.run_count = (workflow.run_count or 0) + 1
        workflow.last_run = datetime.utcnow()
        
        await db.commit()
        return run
    
    async def _execute_node(
        self,
        node: Dict,
        all_nodes: List[Dict],
        connections: List[Dict],
        context: Dict,
        run: WorkflowRun,
        db: AsyncSession
    ) -> Optional[str]:
        """Execute a single node and return next node ID"""
        node_id = node["id"]
        node_type = node["type"]
        node_data = node.get("data", {})
        
        # Log execution
        log_entry = {
            "node_id": node_id,
            "node_type": node_type,
            "started_at": datetime.utcnow().isoformat(),
            "status": "running"
        }
        run.execution_log.append(log_entry)
        await db.commit()
        
        try:
            # Execute node handler
            handler = self.node_handlers.get(node_type)
            if handler:
                result = await handler(node_data, context, db)
                log_entry["result"] = result
                log_entry["status"] = "completed"
            else:
                log_entry["status"] = "skipped"
                log_entry["message"] = f"Unknown node type: {node_type}"
            
        except Exception as e:
            log_entry["status"] = "failed"
            log_entry["error"] = str(e)
            raise
        
        finally:
            log_entry["completed_at"] = datetime.utcnow().isoformat()
            await db.commit()
        
        # Find and execute next nodes
        next_connections = [c for c in connections if c["source_id"] == node_id]
        
        for conn in next_connections:
            next_node = next((n for n in all_nodes if n["id"] == conn["target_id"]), None)
            if next_node:
                # Check if condition passed (for conditional branches)
                handle = conn.get("source_handle")
                if handle and node_type == "condition":
                    condition_result = log_entry.get("result", {}).get("passed", True)
                    if (handle == "true" and not condition_result) or (handle == "false" and condition_result):
                        continue
                
                await self._execute_node(next_node, all_nodes, connections, context, run, db)
        
        return None
    
    async def _handle_condition(self, data: Dict, context: Dict, db: AsyncSession) -> Dict:
        """Evaluate a condition"""
        field = data.get("field", "")
        operator = data.get("operator", "equals")
        value = data.get("value", "")
        
        # Get actual value from context
        actual_value = context.get("variables", {}).get(field) or context.get("trigger_data", {}).get(field)
        
        # Evaluate condition
        passed = False
        if operator == "equals":
            passed = str(actual_value) == str(value)
        elif operator == "contains":
            passed = str(value) in str(actual_value)
        elif operator == "greater_than":
            try:
                passed = float(actual_value) > float(value)
            except:
                passed = False
        elif operator == "less_than":
            try:
                passed = float(actual_value) < float(value)
            except:
                passed = False
        
        return {"passed": passed, "field": field, "actual_value": actual_value}
    
    async def _handle_action(self, data: Dict, context: Dict, db: AsyncSession) -> Dict:
        """Execute a generic action"""
        action_type = data.get("type", "")
        return {"action": action_type, "executed": True}
    
    async def _handle_delay(self, data: Dict, context: Dict, db: AsyncSession) -> Dict:
        """Add a delay"""
        seconds = data.get("seconds", 0)
        minutes = data.get("minutes", 0)
        total_seconds = seconds + (minutes * 60)
        
        if total_seconds > 0:
            await asyncio.sleep(min(total_seconds, 300))  # Max 5 minutes
        
        return {"delayed": total_seconds}
    
    async def _handle_ai_response(self, data: Dict, context: Dict, db: AsyncSession) -> Dict:
        """Generate AI response"""
        prompt = data.get("prompt", "")
        
        # Substitute variables
        for key, value in context.get("variables", {}).items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        response = await ai_service.chat(prompt)
        context["variables"]["ai_response"] = response
        
        return {"response": response}
    
    async def _handle_send_message(self, data: Dict, context: Dict, db: AsyncSession) -> Dict:
        """Send a message"""
        content = data.get("content", "")
        
        # Substitute variables
        for key, value in context.get("variables", {}).items():
            content = content.replace(f"{{{key}}}", str(value))
        
        # In real implementation, this would send via the appropriate platform
        return {"message_sent": True, "content": content}
    
    async def _handle_update_tag(self, data: Dict, context: Dict, db: AsyncSession) -> Dict:
        """Update tags on conversation/customer"""
        action = data.get("action", "add")  # add or remove
        tag = data.get("tag", "")
        
        return {"tag_action": action, "tag": tag}
    
    async def _handle_create_order(self, data: Dict, context: Dict, db: AsyncSession) -> Dict:
        """Create an order"""
        # In real implementation, this would create an order
        return {"order_created": True}
    
    async def check_triggers(
        self,
        trigger_type: str,
        trigger_data: Dict,
        team_id: str,
        db: AsyncSession
    ) -> List[Workflow]:
        """Find workflows matching the trigger"""
        from sqlalchemy import select
        
        result = await db.execute(
            select(Workflow).where(
                Workflow.team_id == team_id,
                Workflow.is_active == True
            )
        )
        workflows = result.scalars().all()
        
        matching = []
        for workflow in workflows:
            trigger = workflow.trigger or {}
            if trigger.get("type") == trigger_type:
                # Check additional trigger conditions
                config = trigger.get("config", {})
                if self._matches_trigger_config(config, trigger_data):
                    matching.append(workflow)
        
        return matching
    
    def _matches_trigger_config(self, config: Dict, trigger_data: Dict) -> bool:
        """Check if trigger data matches config conditions"""
        for key, value in config.items():
            if key in trigger_data and trigger_data[key] != value:
                return False
        return True


# Singleton instance
workflow_engine = WorkflowEngine()
