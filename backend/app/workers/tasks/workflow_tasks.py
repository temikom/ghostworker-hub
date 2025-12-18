"""Workflow execution background tasks"""
from celery import shared_task
from sqlalchemy import select
from datetime import datetime
import structlog

from app.db.session import SyncSessionLocal
from app.models import (
    Workflow, WorkflowRun, Conversation, Message,
    Customer, Order, Tag, ConversationTag
)
from app.models.assistant import TaskStatus

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3)
def execute_workflow(self, workflow_id: str, trigger_data: dict):
    """Execute a workflow with the given trigger data"""
    try:
        with SyncSessionLocal() as db:
            workflow = db.execute(
                select(Workflow).where(Workflow.id == workflow_id)
            ).scalar_one_or_none()
            
            if not workflow or not workflow.is_active:
                logger.warning("workflow_not_active", workflow_id=workflow_id)
                return
            
            # Create workflow run
            run = WorkflowRun(
                workflow_id=workflow.id,
                status=TaskStatus.IN_PROGRESS,
                trigger_data=trigger_data,
                started_at=datetime.utcnow()
            )
            db.add(run)
            db.flush()
            
            execution_log = []
            
            try:
                # Get nodes and connections
                nodes = workflow.nodes or []
                connections = workflow.connections or []
                
                # Build node map
                node_map = {node['id']: node for node in nodes}
                
                # Build connection map (from_node -> [to_nodes])
                conn_map = {}
                for conn in connections:
                    from_node = conn.get('from')
                    to_node = conn.get('to')
                    if from_node not in conn_map:
                        conn_map[from_node] = []
                    conn_map[from_node].append(to_node)
                
                # Find start node
                start_node = None
                for node in nodes:
                    if node.get('type') == 'start' or node.get('id') == 'start':
                        start_node = node
                        break
                
                if not start_node:
                    raise ValueError("No start node found in workflow")
                
                # Execute workflow nodes
                context = {'trigger': trigger_data}
                current_nodes = [start_node['id']]
                
                while current_nodes:
                    next_nodes = []
                    
                    for node_id in current_nodes:
                        node = node_map.get(node_id)
                        if not node:
                            continue
                        
                        result = execute_node(db, node, context)
                        execution_log.append({
                            'node_id': node_id,
                            'type': node.get('type'),
                            'result': result,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        
                        # Update context with result
                        context[node_id] = result
                        
                        # Get next nodes
                        if result.get('continue', True):
                            next_nodes.extend(conn_map.get(node_id, []))
                    
                    current_nodes = next_nodes
                
                # Complete workflow run
                run.status = TaskStatus.COMPLETED
                run.execution_log = execution_log
                run.completed_at = datetime.utcnow()
                
                # Update workflow stats
                workflow.run_count += 1
                workflow.last_run = datetime.utcnow()
                
                db.commit()
                logger.info("workflow_completed", workflow_id=workflow_id, run_id=str(run.id))
                
            except Exception as e:
                run.status = TaskStatus.FAILED
                run.error_message = str(e)
                run.execution_log = execution_log
                run.completed_at = datetime.utcnow()
                db.commit()
                raise
                
    except Exception as e:
        logger.error("workflow_execution_failed", workflow_id=workflow_id, error=str(e))
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


def execute_node(db, node: dict, context: dict) -> dict:
    """Execute a single workflow node"""
    node_type = node.get('type', '')
    config = node.get('config', {})
    
    handlers = {
        'start': handle_start_node,
        'end': handle_end_node,
        'condition': handle_condition_node,
        'action': handle_action_node,
        'delay': handle_delay_node,
        'send_message': handle_send_message_node,
        'update_tag': handle_update_tag_node,
        'ai_response': handle_ai_response_node,
        'create_order': handle_create_order_node,
        'webhook': handle_webhook_node,
    }
    
    handler = handlers.get(node_type, handle_unknown_node)
    return handler(db, config, context)


def handle_start_node(db, config: dict, context: dict) -> dict:
    """Handle start node - just pass through"""
    return {'continue': True}


def handle_end_node(db, config: dict, context: dict) -> dict:
    """Handle end node - stop execution"""
    return {'continue': False}


def handle_condition_node(db, config: dict, context: dict) -> dict:
    """Handle condition node - evaluate condition"""
    conditions = config.get('conditions', [])
    
    for condition in conditions:
        field = condition.get('field', '')
        operator = condition.get('operator', 'equals')
        value = condition.get('value')
        
        # Get field value from context
        field_value = get_nested_value(context, field)
        
        # Evaluate condition
        if operator == 'equals' and field_value == value:
            continue
        elif operator == 'not_equals' and field_value != value:
            continue
        elif operator == 'contains' and value in str(field_value):
            continue
        elif operator == 'greater_than' and float(field_value) > float(value):
            continue
        elif operator == 'less_than' and float(field_value) < float(value):
            continue
        else:
            return {'continue': False, 'matched': False}
    
    return {'continue': True, 'matched': True}


def handle_action_node(db, config: dict, context: dict) -> dict:
    """Handle generic action node"""
    action_type = config.get('action_type', '')
    
    if action_type == 'update_customer':
        # Update customer metadata
        customer_id = context.get('trigger', {}).get('customer_id')
        updates = config.get('updates', {})
        if customer_id:
            customer = db.execute(
                select(Customer).where(Customer.id == customer_id)
            ).scalar_one_or_none()
            if customer:
                for key, value in updates.items():
                    if hasattr(customer, key):
                        setattr(customer, key, value)
    
    elif action_type == 'assign_conversation':
        # Assign conversation to a user
        conv_id = context.get('trigger', {}).get('conversation_id')
        user_id = config.get('user_id')
        if conv_id and user_id:
            conv = db.execute(
                select(Conversation).where(Conversation.id == conv_id)
            ).scalar_one_or_none()
            if conv:
                conv.assigned_to = user_id
    
    return {'continue': True, 'action_type': action_type}


def handle_delay_node(db, config: dict, context: dict) -> dict:
    """Handle delay node - pause execution"""
    delay_seconds = config.get('delay_seconds', 0)
    delay_type = config.get('delay_type', 'seconds')
    
    if delay_type == 'minutes':
        delay_seconds *= 60
    elif delay_type == 'hours':
        delay_seconds *= 3600
    elif delay_type == 'days':
        delay_seconds *= 86400
    
    # In a real implementation, you'd schedule the next node
    # For now, we'll just log the delay
    return {'continue': True, 'delay_seconds': delay_seconds}


def handle_send_message_node(db, config: dict, context: dict) -> dict:
    """Handle send message node"""
    conv_id = context.get('trigger', {}).get('conversation_id')
    message_content = config.get('message', '')
    
    # Interpolate variables in message
    for key, value in context.get('trigger', {}).items():
        message_content = message_content.replace(f'{{{{{key}}}}}', str(value))
    
    if conv_id:
        # Create outbound message
        from app.models import MessageDirection, MessageStatus
        
        conv = db.execute(
            select(Conversation).where(Conversation.id == conv_id)
        ).scalar_one_or_none()
        
        if conv:
            message = Message(
                conversation_id=conv.id,
                platform=conv.platform,
                direction=MessageDirection.OUTBOUND,
                sender='system',
                content=message_content,
                status=MessageStatus.PENDING
            )
            db.add(message)
            
            return {'continue': True, 'message_id': str(message.id)}
    
    return {'continue': True, 'error': 'No conversation found'}


def handle_update_tag_node(db, config: dict, context: dict) -> dict:
    """Handle update tag node - add or remove tags"""
    action = config.get('action', 'add')  # add or remove
    tag_id = config.get('tag_id')
    target = config.get('target', 'conversation')  # conversation or customer
    
    if target == 'conversation':
        conv_id = context.get('trigger', {}).get('conversation_id')
        if conv_id and tag_id:
            if action == 'add':
                # Check if tag already exists
                existing = db.execute(
                    select(ConversationTag).where(
                        ConversationTag.conversation_id == conv_id,
                        ConversationTag.tag_id == tag_id
                    )
                ).scalar_one_or_none()
                
                if not existing:
                    tag_assoc = ConversationTag(
                        conversation_id=conv_id,
                        tag_id=tag_id
                    )
                    db.add(tag_assoc)
            else:
                # Remove tag
                db.execute(
                    select(ConversationTag).where(
                        ConversationTag.conversation_id == conv_id,
                        ConversationTag.tag_id == tag_id
                    )
                )
    
    return {'continue': True, 'action': action, 'tag_id': tag_id}


def handle_ai_response_node(db, config: dict, context: dict) -> dict:
    """Handle AI response node - generate AI response"""
    prompt = config.get('prompt', '')
    model = config.get('model', 'gpt-4o-mini')
    
    # Get conversation context
    conv_id = context.get('trigger', {}).get('conversation_id')
    
    if conv_id:
        # Get recent messages for context
        messages = db.execute(
            select(Message).where(
                Message.conversation_id == conv_id
            ).order_by(Message.created_at.desc()).limit(10)
        ).scalars().all()
        
        # Build context for AI
        conversation_context = [
            {'role': 'user' if m.direction.value == 'inbound' else 'assistant', 'content': m.content}
            for m in reversed(messages)
        ]
        
        # In production, call OpenAI API here
        # For now, return placeholder
        return {
            'continue': True,
            'ai_response': f"AI response placeholder for prompt: {prompt}"
        }
    
    return {'continue': True, 'error': 'No conversation context'}


def handle_create_order_node(db, config: dict, context: dict) -> dict:
    """Handle create order node"""
    customer_id = context.get('trigger', {}).get('customer_id')
    conv_id = context.get('trigger', {}).get('conversation_id')
    
    if customer_id:
        # Get customer's team
        customer = db.execute(
            select(Customer).where(Customer.id == customer_id)
        ).scalar_one_or_none()
        
        if customer:
            from decimal import Decimal
            
            order = Order(
                team_id=customer.team_id,
                customer_id=customer_id,
                conversation_id=conv_id,
                subtotal=Decimal('0.00'),
                total=Decimal('0.00')
            )
            db.add(order)
            db.flush()
            
            return {'continue': True, 'order_id': str(order.id)}
    
    return {'continue': True, 'error': 'Could not create order'}


def handle_webhook_node(db, config: dict, context: dict) -> dict:
    """Handle webhook node - call external webhook"""
    import requests
    
    url = config.get('url', '')
    method = config.get('method', 'POST')
    headers = config.get('headers', {})
    
    if url:
        try:
            if method == 'POST':
                response = requests.post(url, json=context, headers=headers, timeout=30)
            else:
                response = requests.get(url, params=context.get('trigger', {}), headers=headers, timeout=30)
            
            return {
                'continue': True,
                'status_code': response.status_code,
                'response': response.text[:500]
            }
        except Exception as e:
            return {'continue': True, 'error': str(e)}
    
    return {'continue': True, 'error': 'No webhook URL configured'}


def handle_unknown_node(db, config: dict, context: dict) -> dict:
    """Handle unknown node type"""
    return {'continue': True, 'warning': 'Unknown node type'}


def get_nested_value(obj: dict, path: str):
    """Get nested value from dict using dot notation"""
    keys = path.split('.')
    value = obj
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


@shared_task
def trigger_workflow_on_event(event_type: str, event_data: dict):
    """Trigger workflows based on events"""
    with SyncSessionLocal() as db:
        team_id = event_data.get('team_id')
        
        if not team_id:
            return
        
        # Find active workflows with matching trigger
        workflows = db.execute(
            select(Workflow).where(
                Workflow.team_id == team_id,
                Workflow.is_active == True
            )
        ).scalars().all()
        
        for workflow in workflows:
            trigger = workflow.trigger or {}
            trigger_type = trigger.get('type')
            
            if trigger_type == event_type:
                # Check trigger conditions
                conditions = trigger.get('conditions', [])
                should_trigger = True
                
                for condition in conditions:
                    field = condition.get('field', '')
                    operator = condition.get('operator', 'equals')
                    value = condition.get('value')
                    
                    field_value = get_nested_value(event_data, field)
                    
                    if operator == 'equals' and field_value != value:
                        should_trigger = False
                        break
                    elif operator == 'contains' and value not in str(field_value):
                        should_trigger = False
                        break
                
                if should_trigger:
                    execute_workflow.delay(str(workflow.id), event_data)
                    logger.info("workflow_triggered", workflow_id=str(workflow.id), event_type=event_type)
