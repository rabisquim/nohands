import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Desativa carregamento real do modelo durante testes rápidos de rota
os.environ["PARAKEET_MODEL"] = "none"

from server import app


class ServerStaticFilesTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_root_serves_index_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("Ditador por Voz", response.text)

    def test_health_endpoint_still_works(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
