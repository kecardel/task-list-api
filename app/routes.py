from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request, make_response
from datetime import datetime
import os
import requests

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("/<goal_id>/tasks", methods=["POST"], strict_slashes=False)
def assign_tasks_to_one_goal(goal_id):
    request_body = request.get_json()

    goal = Goal.query.get(goal_id)

    task_ids = request_body["task_ids"]

    for task_id in task_ids:
        task = Task.query.get(task_id)
        goal.tasks.append(task)
        
    db.session.commit()

    return make_response({
        "id": goal.goal_id,   
        "task_ids": task_ids     
    }, 200)


@goals_bp.route("/<goal_id>/tasks", methods=["GET"], strict_slashes=False)
def get_tasks_from_goal_id(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    tasks = goal.tasks

    tasks_response = []

    for task in tasks:
        tasks_response.append(task.to_json())
    
    goal_response = goal.to_json()
    goal_response["tasks"] = tasks_response

    return goal_response, 200
0
@goals_bp.route("", methods=["POST"], strict_slashes=False)
def create_goal():
    request_body = request.get_json()
    
    try:
        new_goal = Goal(title=request_body["title"])

    except KeyError:
        return make_response({
            "details": "Invalid data"
        }, 400)

    db.session.add(new_goal)
    db.session.commit()

    return {
        "goal": new_goal.to_json()
    }, 201

@goals_bp.route("/<goal_id>", methods=["GET"], strict_slashes=False)
def get_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    return {
        "goal": goal.to_json()}, 200

@goals_bp.route("", methods=["GET"], strict_slashes=False)
def goals_index():
    goals = Goal.query.all()
    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_json())

    return jsonify(goals_response), 200

@goals_bp.route("/<goal_id>", methods=["PUT"], strict_slashes=False)
def update_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    form_data = request.get_json()
    
    goal.title = form_data["title"]

    db.session.commit()

    return {
        "goal": goal.to_json()
    }, 200

@goals_bp.route("/<goal_id>", methods=["DELETE"], strict_slashes=False)
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    db.session.delete(goal)
    db.session.commit()

    return make_response({
        "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
    })


@tasks_bp.route("", methods=["GET"], strict_slashes=False) 
def tasks_index():
    sort_type = request.args.get("sort")

    if sort_type == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    elif sort_type == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    else:
        tasks = Task.query.all()
    
    tasks_response = []

    for task in tasks:
        tasks_response.append(task.to_json())

    return jsonify(tasks_response), 200
    
@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_one_task(task_id):
    task = Task.query.get_or_404(task_id)

    return {
        "task": task.to_json()}, 200
        
@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])

    except KeyError:
        return make_response({
            "details": "Invalid data"
        }, 400)

    db.session.add(new_task)
    db.session.commit()

    return {
        "task": new_task.to_json()
    }, 201

@tasks_bp.route("/<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    form_data = request.get_json()

    task.title = form_data["title"]
    task.description = form_data["description"]
    task.is_complete = form_data["completed_at"]

    db.session.commit()

    return {
        "task": task.to_json()
    }, 200

@tasks_bp.route("/<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    db.session.delete(task)
    db.session.commit()

    return make_response({
        "details": f'Task {task.task_id} "{task.title}" successfully deleted'
    })

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"], strict_slashes=False)
def task_mark_complete(task_id):
    task = Task.query.get_or_404(task_id)
    current_datetime = datetime.utcnow()
    
    task.completed_at = current_datetime
    
    db.session.commit()

    response = requests.get('https://slack.com/api/chat.postMessage',\
            params={
            "channel": "task-notifications",
            "text": f"Someone just completed the task {task.title}"},
            headers={'Authorization': os.environ['SLACK_TOKEN']})
            
    return {
        "task": task.to_json()
    }, 200

    
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"], strict_slashes=False)
def task_mark_incomplete(task_id):
    task = Task.query.get_or_404(task_id)

    if task.completed_at != None:
        task.completed_at = None

    db.session.commit()

    return {
        "task": task.to_json()
    }, 200