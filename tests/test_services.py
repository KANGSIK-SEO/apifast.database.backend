import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from auth.passwords import hash_password
from database import Base
from models import Project, Task, User
from services import auth_service, project_service, task_service


class TaskBoardServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.db: Session = self.session_factory()
        self.user = User(
            email="alice@example.com",
            name="앨리스",
            password_hash=hash_password("alice1234"),
        )
        self.other_user = User(
            email="bob@example.com",
            name="밥",
            password_hash=hash_password("bob1234"),
        )
        self.db.add_all([self.user, self.other_user])
        self.db.commit()
        self.project = project_service.create_project(
            self.db,
            self.user.id,
            "학습",
            "백엔드 공부",
        )

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_authentication_verifies_password_hash(self):
        self.assertEqual(
            auth_service.authenticate(self.db, "ALICE@example.com", "alice1234").id,
            self.user.id,
        )
        self.assertIsNone(
            auth_service.authenticate(self.db, "alice@example.com", "wrong-password")
        )
        self.assertNotIn("alice1234", self.user.password_hash)

    def test_owner_can_create_and_toggle_task(self):
        task = task_service.create_task(
            self.db,
            self.user.id,
            self.project.id,
            "테스트 작성",
            "서비스 테스트",
        )
        self.assertEqual(task.status, "in_progress")
        self.assertEqual(task_service.toggle_task_status(self.db, self.user.id, self.project.id, task.id).status, "completed")
        self.assertEqual(task_service.toggle_task_status(self.db, self.user.id, self.project.id, task.id).status, "in_progress")
        self.assertEqual(project_service.get_project(self.db, self.project.id, self.user.id).tasks[0].title, "테스트 작성")

    def test_other_user_cannot_read_or_add_to_project(self):
        with self.assertRaises(HTTPException) as error:
            project_service.get_project(self.db, self.project.id, self.other_user.id)
        self.assertEqual(error.exception.status_code, 404)

        with self.assertRaises(HTTPException) as error:
            task_service.create_task(self.db, self.other_user.id, self.project.id, "타인 작업", "")
        self.assertEqual(error.exception.status_code, 404)

    def test_task_cannot_be_toggled_through_another_project_url(self):
        task = task_service.create_task(self.db, self.user.id, self.project.id, "보호 작업", "")
        another_project = project_service.create_project(
            self.db,
            self.user.id,
            "다른 프로젝트",
            "",
        )
        with self.assertRaises(HTTPException) as error:
            task_service.toggle_task_status(
                self.db,
                self.user.id,
                another_project.id,
                task.id,
            )
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(self.db.get(Task, task.id).status, "in_progress")

    def test_parent_deletion_cascades_to_related_records(self):
        task = task_service.create_task(self.db, self.user.id, self.project.id, "삭제 대상", "")
        task_id = task.id
        project_id = self.project.id
        self.db.delete(self.project)
        self.db.commit()
        self.assertIsNone(self.db.get(Project, project_id))
        self.assertIsNone(self.db.get(Task, task_id))


if __name__ == "__main__":
    unittest.main()
