from unittest.mock import patch

from paramiko import RSAKey, SSHClient


def test_flag_submitter(simulation_container):
    flag_submitter = simulation_container.flag_submitter()

    flags = ["ENO123123123123", "ENO321321321321", "ENO231231231231231"]

    with patch.object(RSAKey, "from_private_key_file"):
        with patch.object(SSHClient, "connect") as mock_connect:
            with patch.object(SSHClient, "get_transport") as mock_get_transport:
                flag_submitter.submit_flags("10.1.1.1", flags)

        mock_connect.assert_called_once_with(
            hostname="234.123.12.32",
            username="root",
            pkey=RSAKey.from_private_key_file("/path/to/your/private_key"),
        )

    mock_get_transport.assert_called_once()

    mock_get_transport.return_value.open_channel.assert_called_once_with(
        "direct-tcpip", ("10.1.5.1", 1337), ("localhost", 0)
    )

    # mock_get_transport.return_value.open_channel.return_value.send.assert_called_once_with(
    #     b"ENO123123123123\nENO321321321321\nENO231231231231231\n"
    # )
