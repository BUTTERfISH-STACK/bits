# services/temporal/sample_workflow.py
from temporalio import workflow, activity

@activity.defn
async def send_email(activity_input):
    # Implement email sending via SMTP/Twilio/SES
    return {"status":"sent"}

@workflow.defn
class AutomationWorkflow:
    @workflow.run
    async def run(self, instruction: dict):
        # instruction: {action: 'send_email', payload: {...}}
        if instruction['action'] == 'send_email':
            result = await workflow.execute_activity(send_email, instruction['payload'], start_to_close_timeout=timedelta(seconds=30))
            return result
        return {"status":"unknown"}
