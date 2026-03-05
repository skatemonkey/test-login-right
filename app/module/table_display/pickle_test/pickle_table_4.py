import pickle
import random
import time

# Initial data structure
table_data = {
    "schema": [
        {
            "name": "Model 1",
            "features": [
                {"name": "Feature 1", "tasks": ["Task 1", "Task 2"], "owner": "owner 1"},
                {"name": "Feature 2", "tasks": ["Task 1", "Task 2"], "owner": "owner 2"}
            ]
        },
        {
            "name": "Model 2",
            "features": [
                {"name": "Feature 1", "tasks": ["Task 1", "Task 2"], "owner": None},
                {"name": "Feature 2", "tasks": ["Task 1", "Task 2"], "owner": None},
                {"name": "Feature 3", "tasks": ["Task 1", "Task 2"], "owner": None}
            ]
        }
    ]
}

pickle_path = "/Users/user/hub/dev/test/output/table_4.pkl"
counter = 0


def random_modify(data):
    action = random.choice(["add_task", "remove_task", "add_feature", "remove_feature", "add_model", "remove_model"])

    if action == "add_task" and data["schema"]:
        model = random.choice(data["schema"])
        if model["features"]:
            feature = random.choice(model["features"])
            task_num = len(feature["tasks"]) + 1
            feature["tasks"].append(f"Task {task_num}")
            print(f"Added Task {task_num} to {model['name']} > {feature['name']}")

    elif action == "remove_task" and data["schema"]:
        model = random.choice(data["schema"])
        if model["features"]:
            feature = random.choice(model["features"])
            if len(feature["tasks"]) > 1:
                removed = feature["tasks"].pop()
                print(f"Removed {removed} from {model['name']} > {feature['name']}")

    elif action == "add_feature" and data["schema"]:
        model = random.choice(data["schema"])
        feature_num = len(model["features"]) + 1
        model["features"].append({
            "name": f"Feature {feature_num}",
            "tasks": ["Task 1"],
            "owner": None
        })
        print(f"Added Feature {feature_num} to {model['name']}")

    elif action == "remove_feature" and data["schema"]:
        model = random.choice(data["schema"])
        if len(model["features"]) > 1:
            removed = model["features"].pop()
            print(f"Removed {removed['name']} from {model['name']}")

    elif action == "add_model":
        model_num = len(data["schema"]) + 1
        data["schema"].append({
            "name": f"Model {model_num}",
            "features": [{"name": "Feature 1", "tasks": ["Task 1"], "owner": None}]
        })
        print(f"Added Model {model_num}")

    elif action == "remove_model" and len(data["schema"]) > 1:
        removed = data["schema"].pop()
        print(f"Removed {removed['name']}")

    else:
        print("No modification made")


while True:
    random_modify(table_data)

    with open(pickle_path, "wb") as f:
        pickle.dump(table_data, f)

    print(f"Iteration {counter}, saved to {pickle_path}\n")

    counter += 1
    time.sleep(3)