import sys
import os

print("Current Working Directory:", os.getcwd())
print("Python Path:", sys.path)

# Test importing tasks and neo4j
try:
    from app.routes import tasks, neo4j
    print("Imports successful for app.routes.tasks and app.routes.neo4j")
except Exception as e:
    print("Import Error:", str(e))

# Test importing the entire app package
try:
    import app
    print("App module imported successfully!")
except Exception as e:
    print("App Module Import Error:", str(e))
