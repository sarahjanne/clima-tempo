from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

from services.clima import consultar_clima_por_cep


class ConsultarClimaPorCepTests(TestCase):
    @patch("services.clima.requests.get")
    def test_consulta_previsao_por_data_nao_inclui_current_weather(self, mock_get):
        resposta_cep = Mock()
        resposta_cep.status_code = 200
        resposta_cep.json.return_value = {
            "location": {
                "coordinates": {
                    "latitude": "-23.55",
                    "longitude": "-46.63",
                }
            }
        }

        resposta_clima = Mock()
        resposta_clima.status_code = 200
        resposta_clima.json.return_value = {
            "daily": {
                "temperature_2m_max": [25.0],
                "wind_speed_10m_max": [12.0],
            },
            "daily_units": {
                "temperature_2m_max": "C",
                "wind_speed_10m_max": "km/h",
            },
        }

        mock_get.side_effect = [resposta_cep, resposta_clima]

        consultar_clima_por_cep("01001000", date(2026, 9, 24))

        url_clima = mock_get.call_args_list[1].args[0]

        self.assertIn("start_date=2026-09-24", url_clima)
        self.assertIn("end_date=2026-09-24", url_clima)
        self.assertIn("daily=temperature_2m_max,wind_speed_10m_max", url_clima)
        self.assertNotIn("current_weather=true", url_clima)
