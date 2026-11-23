import sys
import types
import unittest
from unittest.mock import MagicMock, patch
import models
from exceptions import ValidationError
from models.seed_data import CAREER_PATHS, RESOURCES

#temporary mock modules until Sadia's models/career_paths.py and models/resources.py merge
if not hasattr(models, "career_paths"):
    fakeCareerPaths=types.ModuleType("models.career_paths")
    fakeCareerPaths.list_career_paths=lambda conn: sorted(CAREER_PATHS, key=lambda p: p["position"])
    sys.modules["models.career_paths"]=fakeCareerPaths
    models.career_paths=fakeCareerPaths

if not hasattr(models, "resources"):
    fakeResources=types.ModuleType("models.resources")
    def _fakeListResources(conn, category=None):
        items=sorted(RESOURCES, key=lambda r: r["position"])
        if category is None:
            return items
        return [r for r in items if r["category"]==category]
    fakeResources.list_resources=_fakeListResources
    sys.modules["models.resources"]=fakeResources
    models.resources=fakeResources

import controllers.content as contentController


class TestContentController(unittest.TestCase):

    def setUp(self):
        #mock db connection so tests never touch devoyage.db
        self.fakeConn=MagicMock()
        self.connectionPatcher=patch(
            "controllers.content.db.get_connection",
            return_value=self.fakeConn,
        )
        self.connectionPatcher.start()

    def tearDown(self):
        self.connectionPatcher.stop()

    #test career paths returns all 4 seeded paths in position order
    def test_list_career_paths_returns_seeded_paths_in_order(self):
        paths=contentController.list_career_paths()

        self.assertEqual(len(paths), 4)

        positions=[p["position"] for p in paths]
        self.assertEqual(positions, sorted(positions))

        slugs={p["slug"] for p in paths}
        self.assertEqual(slugs, {"software_engineering", "data", "security", "machine_learning"})

        for path in paths:
            self.assertIsInstance(path["skills"], list)
            self.assertIsInstance(path["first_steps"], list)

        self.fakeConn.close.assert_called_once()

    #test resources returns all seeded items in position order
    def test_list_resources_returns_all_seeded_resources(self):
        resources=contentController.list_resources()

        self.assertGreaterEqual(len(resources), 10)

        positions=[r["position"] for r in resources]
        self.assertEqual(positions, sorted(positions))
        self.fakeConn.close.assert_called_once()

    #test category filter only returns matching resources
    def test_list_resources_filters_by_valid_category(self):
        learningResources=contentController.list_resources("learning")

        self.assertGreaterEqual(len(learningResources), 1)
        for resource in learningResources:
            self.assertEqual(resource["category"], "learning")

    #test unknown category raises ValidationError without opening db
    def test_list_resources_rejects_unknown_category(self):
        with self.assertRaises(ValidationError):
            contentController.list_resources("invalid_category")

        self.fakeConn.close.assert_not_called()


if __name__=="__main__":
    unittest.main()