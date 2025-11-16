"""
Background Scheduler for Agents
Manages periodic tasks like BountyHunter2's 24-hour news scraping
"""

import asyncio
from datetime import datetime, timedelta
from typing import Callable, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentScheduler:
    """
    Scheduler for running agent tasks periodically
    """

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running = False

    def add_task(
        self,
        task_id: str,
        task_func: Callable,
        interval_hours: int,
        run_immediately: bool = False
    ):
        """Add a scheduled task"""
        self.tasks[task_id] = {
            "func": task_func,
            "interval": timedelta(hours=interval_hours),
            "last_run": None,
            "run_immediately": run_immediately
        }
        logger.info(f"📅 Scheduled task '{task_id}' to run every {interval_hours} hours")

    async def start(self):
        """Start the scheduler"""
        self.running = True
        logger.info("⏰ Agent scheduler started")

        while self.running:
            for task_id, task_info in self.tasks.items():
                func = task_info["func"]
                interval = task_info["interval"]
                last_run = task_info["last_run"]
                run_immediately = task_info.get("run_immediately", False)

                # Check if task should run
                should_run = False

                if run_immediately and last_run is None:
                    should_run = True
                    task_info["run_immediately"] = False
                elif last_run is None:
                    should_run = True
                elif datetime.now() - last_run >= interval:
                    should_run = True

                if should_run:
                    try:
                        logger.info(f"🔄 Running scheduled task: {task_id}")
                        await func()
                        task_info["last_run"] = datetime.now()
                        logger.info(f"✅ Task '{task_id}' completed")
                    except Exception as e:
                        logger.error(f"❌ Error in task '{task_id}': {e}")

            # Sleep for 1 hour before checking again
            await asyncio.sleep(3600)  # Check every hour

    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("⏹️ Agent scheduler stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.running,
            "tasks": {
                task_id: {
                    "last_run": task_info["last_run"].isoformat() if task_info["last_run"] else None,
                    "interval_hours": task_info["interval"].total_seconds() / 3600
                }
                for task_id, task_info in self.tasks.items()
            }
        }


# Global scheduler instance
agent_scheduler = AgentScheduler()
