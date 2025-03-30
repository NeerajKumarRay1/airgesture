import os

def create_directory_structure():
    # Define the directory structure
    directories = [
        'src',
        'src/ui',
        'src/ui/components',
        'src/ui/styles',
        'src/gestures',
        'src/utils',
        'src/config',
        'tests'
    ]
    
    # Create directories
    for dir in directories:
        os.makedirs(dir, exist_ok=True)
        # Create __init__.py in each directory
        with open(os.path.join(dir, '__init__.py'), 'w') as f:
            pass

    # Create other necessary files
    open('requirements.txt', 'w').close()
    open('README.md', 'w').close()
    open('.gitignore', 'w').close()

create_directory_structure() 