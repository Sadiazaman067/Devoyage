import os
import tempfile
import unittest
from unittest.mock import patch
import controllers.content as contentController
from exceptions import ValidationError
from models import db


class TestContentController(unittest.TestCase):

    def setUp(self):
        #create temp dir and db so real devoyage.db is never touched
        self.tempDir=tempfile.TemporaryDirectory()
        self.dbPath=os.path.join(self.tempDir.name, "test_devoyage.db")

        self.realGetConnection=db.get_connection

        #init_db creates tables and seeds career_paths and resources
        conn=self.realGetConnection(self.dbPath)
        db.init_db(conn)
        conn.close()

        #redirect controller db calls to temp db
        self.connectionPatcher=patch(
            "controllers.content.db.get_connection",
            side_effect=self.getTestConnection,
        )
        self.connectionPatcher.start()

    def tearDown(self):
        self.connectionPatcher.stop()
        self.tempDir.cleanup()

    def getTestConnection(self):
        return self.realGetConnection(self.dbPath)

    #test career paths returns all 4 seeded paths in position order
    def test_list_career_paths_returns_seeded_paths_in_order(self):
        paths=contentController.list_career_paths()

        self.assertEqual(len(paths), 4)

        positions=[p["position"] for p in paths]
        self.assertEqual(positions, sorted(positions))

        slugs={p["slug"] for p in paths}
        self.assertEqual(slugs, {"software_engineering", "data", "security", "machine_learning"})

        #skills and first_steps should be decoded back to lists
        for path in paths:
            self.assertIsInstance(path["skills"], list)
            self.assertIsInstance(path["first_steps"], list)

    #test resources returns all seeded items in position order
    def test_list_resources_returns_all_seeded_resources(self):
        resources=contentController.list_resources()

        self.assertGreaterEqual(len(resources), 10)

        positions=[r["position"] for r in resources]
        self.assertEqual(positions, sorted(positions))

    #test category filter only returns matching resources
    def test_list_resources_filters_by_valid_category(self):
        learningResources=contentController.list_resources("learning")

        self.assertGreaterEqual(len(learningResources), 1)
        for resource in learningResources:
            self.assertEqual(resource["category"], "learning")

    #test unknown category raises ValidationError
    def test_list_resources_rejects_unknown_category(self):
        with self.assertRaises(ValidationError):
            contentController.list_resources("invalid_category")


if __name__=="__main__":
    unittest.main()