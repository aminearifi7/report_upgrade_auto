"""
DM Client — SSH fallback via paramiko + ubus-cli.
Used when WebUI automation fails to configure a parameter.
"""
import time
import paramiko
from utils.logger import Logger


class DMClient:
    """
    Connects to the HGW via SSH and executes ubus-cli commands
    as a fallback when WebUI automation fails.

    Usage:
        with DMClient() as dm:
            dm.set_wifi_ssids("amine_prpl_24", "amine_prpl_5ghz", "amine_prpl_6ghz")
    """

    SSH_HOST     = "192.168.3.5"
    SSH_USER     = "root"
    SSH_PASSWORD = "sah"
    SSH_PORT     = 22
    TIMEOUT      = 15  # seconds per command

    def __init__(self):
        self.logger = Logger().get_logger()
        self.client = None

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.disconnect()

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self):
        """Open SSH connection to the HGW."""
        self.logger.info(f"[DM] Connecting to {self.SSH_HOST} via SSH...")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.SSH_HOST,
            port=self.SSH_PORT,
            username=self.SSH_USER,
            password=self.SSH_PASSWORD,
            timeout=10,
            look_for_keys=False,
            allow_agent=False,
        )
        self.logger.info("[DM] SSH connection established.")

    def disconnect(self):
        """Close SSH connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.logger.info("[DM] SSH connection closed.")

    # ------------------------------------------------------------------
    # Core: run commands inside ubus-cli interactive shell
    # ------------------------------------------------------------------

    def run_ubus_commands(self, commands: list[str]) -> bool:
        """
        Opens an interactive ubus-cli shell and runs a list of DM commands.
        Each command is a string like: Device.WiFi.SSID.vap2g0priv.SSID=my_ssid

        Returns True if all commands executed without error, False otherwise.
        """
        if not self.client:
            self.logger.error("[DM] SSH client not connected.")
            return False

        try:
            self.logger.info(f"[DM] Opening ubus-cli shell to run {len(commands)} command(s)...")
            channel = self.client.invoke_shell()
            channel.settimeout(self.TIMEOUT)

            # Wait for shell prompt
            time.sleep(1)
            self._flush(channel)

            # Launch ubus-cli
            channel.send("ubus-cli\n")
            time.sleep(2)
            output = self._read(channel)
            self.logger.info(f"[DM] ubus-cli started. Output: {output.strip()[:200]}")

            # Send each DM command
            for cmd in commands:
                self.logger.info(f"[DM] Sending command: {cmd}")
                channel.send(f"{cmd}\n")
                time.sleep(1.5)
                result = self._read(channel)
                self.logger.info(f"[DM] Response: {result.strip()[:200]}")

                # Basic error detection
                if any(err in result.lower() for err in ["error", "failed", "invalid", "unknown"]):
                    self.logger.error(f"[DM] Command failed: {cmd} → {result.strip()[:200]}")
                    channel.send("exit\n")
                    channel.close()
                    return False

            # Exit ubus-cli cleanly
            channel.send("exit\n")
            time.sleep(0.5)
            channel.close()

            self.logger.info("[DM] All ubus-cli commands executed successfully.")
            return True

        except Exception as e:
            self.logger.error(f"[DM] ubus-cli execution failed: {e}")
            return False

    # ------------------------------------------------------------------
    # WiFi SSID fallback
    # ------------------------------------------------------------------

    def set_wifi_ssids(self, ssid_24: str, ssid_5: str, ssid_6: str) -> bool:
        """Set SSID for all 3 bands via DM (ubus-cli fallback)."""
        self.logger.info(f"[DM] Setting WiFi SSIDs: 2.4={ssid_24} | 5={ssid_5} | 6={ssid_6}")
        commands = [
            f"Device.WiFi.SSID.vap2g0priv.SSID={ssid_24}",
            f"Device.WiFi.SSID.vap5g0priv.SSID={ssid_5}",
            f"Device.WiFi.SSID.vap6g0priv.SSID={ssid_6}",
        ]
        return self.run_ubus_commands(commands)

    def set_wifi_password(self, vap: str, password: str) -> bool:
        """Set WiFi password for a specific VAP via DM."""
        self.logger.info(f"[DM] Setting password for VAP: {vap}")
        commands = [f"Device.WiFi.AccessPoint.{vap}.Security.KeyPassphrase={password}"]
        return self.run_ubus_commands(commands)

    def set_wifi_security(self, vap: str, mode: str = "WPA3-Personal") -> bool:
        """Set WiFi security mode for a specific VAP via DM."""
        self.logger.info(f"[DM] Setting security mode '{mode}' for VAP: {vap}")
        commands = [f"Device.WiFi.AccessPoint.{vap}.Security.ModeEnabled={mode}"]
        return self.run_ubus_commands(commands)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _read(self, channel, delay: float = 0.5) -> str:
        """Read available output from the channel."""
        time.sleep(delay)
        output = ""
        while channel.recv_ready():
            output += channel.recv(4096).decode("utf-8", errors="ignore")
        return output

    def _flush(self, channel):
        """Discard any pending output."""
        self._read(channel)