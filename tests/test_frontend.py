import os
import unittest


class TestFrontendStructure(unittest.TestCase):
    def setUp(self):
        self.html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
        self.assertTrue(os.path.exists(self.html_path), "frontend/index.html deve existir")
        with open(self.html_path, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_vu_meter_elements_present(self):
        """Verifica se os elementos e funções do VU meter estão declarados no frontend."""
        self.assertIn('id="vuContainer"', self.content, "Container do VU meter deve existir")
        self.assertIn('id="vuMeter"', self.content, "Canvas do VU meter deve existir")
        self.assertIn('initAudioVisualizer', self.content, "Função initAudioVisualizer deve existir")
        self.assertIn('stopAudioVisualizer', self.content, "Função stopAudioVisualizer deve existir")

    def test_history_elements_present(self):
        """Verifica se os elementos e funções do histórico estão declarados no frontend."""
        self.assertIn('id="historySection"', self.content, "Seção de histórico deve existir")
        self.assertIn('id="historyList"', self.content, "Lista de histórico deve existir")
        self.assertIn('id="historyCount"', self.content, "Contador de histórico deve existir")
        self.assertIn('parakeet_transcription_history', self.content, "Chave de localStorage correta deve existir")
        self.assertIn('addHistoryEntry', self.content, "Função addHistoryEntry deve existir")
        self.assertIn('deleteHistoryEntry', self.content, "Função deleteHistoryEntry deve existir")
        self.assertIn('clearAllHistory', self.content, "Função clearAllHistory deve existir")

    def test_studio_pro_elements_present(self):
        """Verifica se os novos elementos do design Studio Pro estão presentes."""
        self.assertIn('id="toastContainer"', self.content, "Container de toasts deve existir")
        self.assertIn('id="wordCharCount"', self.content, "Contador de palavras/caracteres deve existir")
        self.assertIn('id="settingsPopover"', self.content, "Popover de conexão deve existir")
        self.assertIn('id="settingsBtn"', self.content, "Botão acionador de configurações deve existir")
        self.assertIn('showToast', self.content, "Função showToast deve existir")


if __name__ == "__main__":
    unittest.main()
