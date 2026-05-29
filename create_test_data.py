import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "team_finder.settings")
django.setup()

from projects.models import Project
from users.models import User


def create_test_data():
    users = []
    user_data = [
        {
            "email": "john@example.com",
            "name": "John",
            "surname": "Developer",
            "phone": "89991234567",
            "password": "testpass123",
            "about": "Full-stack developer with 5 years of experience",
        },
        {
            "email": "jane@example.com",
            "name": "Jane",
            "surname": "Designer",
            "phone": "89991234568",
            "password": "testpass123",
            "about": "UI/UX designer passionate about user experience",
        },
        {
            "email": "bob@example.com",
            "name": "Bob",
            "surname": "Manager",
            "phone": "89991234569",
            "password": "testpass123",
            "about": "Project manager with agile experience",
        },
    ]

    for data in user_data:
        user, created = User.objects.get_or_create(
            email=data["email"],
            defaults={
                "name": data["name"],
                "surname": data["surname"],
                "phone": data["phone"],
                "about": data["about"],
            },
        )
        if created:
            user.set_password(data["password"])
            user.save()
            print(f"Created user: {user.email}")
        users.append(user)

    projects_data = [
        {
            "name": "Django Web App",
            "description": "Build a modern web application using Django and React",
            "owner_idx": 0,
            "status": "open",
            "github_url": "https://github.com/example/django-webapp",
        },
        {
            "name": "Mobile App Development",
            "description": "Create a cross-platform mobile app using Flutter",
            "owner_idx": 0,
            "status": "open",
            "github_url": "https://github.com/example/mobile-app",
        },
        {
            "name": "Design System",
            "description": "Create a comprehensive design system for our company",
            "owner_idx": 1,
            "status": "open",
            "github_url": "https://github.com/example/design-system",
        },
        {
            "name": "Data Analytics Platform",
            "description": "Build an analytics platform for real-time data visualization",
            "owner_idx": 2,
            "status": "open",
            "github_url": "https://github.com/example/analytics",
        },
    ]

    for data in projects_data:
        project, created = Project.objects.get_or_create(
            name=data["name"],
            owner=users[data["owner_idx"]],
            defaults={
                "description": data["description"],
                "status": data["status"],
                "github_url": data["github_url"],
            },
        )
        if created:
            project.participants.add(users[data["owner_idx"]])
            print(f"Created project: {project.name}")

    if len(users) > 1 and Project.objects.exists():
        project = Project.objects.first()
        for user in users[1:]:
            project.participants.add(user)
        print(f"Added participants to {project.name}")

    print("Test data created successfully!")


if __name__ == "__main__":
    create_test_data()
