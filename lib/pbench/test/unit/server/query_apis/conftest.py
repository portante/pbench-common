from typing import Any, Dict
import pytest
import requests
import responses


@pytest.fixture
@responses.activate
def query_api(client, server_config):
    """
    Help controller queries that want to interact with a mocked
    Elasticsearch service.

    This is a fixture which exposes a function of the same name that can be
    used to set up and validate a mocked Elasticsearch query with a JSON
    payload and an expected status.

    Parameters to the mocked Elasticsearch POST are passed as keyword
    parameters: these can be any of the parameters supported by the
    responses mock. Exceptions are specified by providing an Exception()
    instance as the 'body'.

    :return: the response object for further checking
    """

    def query_api(
        pbench_uri: str,
        es_uri: str,
        payload: Dict[str, Any],
        expected_index: str,
        expected_status: str,
        **kwargs,
    ) -> requests.Response:
        host = server_config.get("elasticsearch", "host")
        port = server_config.get("elasticsearch", "port")
        es_url = f"http://{host}:{port}{expected_index}{es_uri}"
        with responses.RequestsMock() as rsp:
            rsp.add(responses.POST, es_url, **kwargs)
            response = client.post(
                f"{server_config.rest_uri}{pbench_uri}", json=payload
            )
            assert rsp.assert_call_count(es_url, 1) is True
        assert response.status_code == expected_status
        return response

    return query_api