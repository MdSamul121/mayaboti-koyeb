export function linearManifestUrl(
  publicBaseUrl: string,
  webhookPath: string,
  callbackPath: string,
): string {
  const manifest = {
    $schema: "https://linear.app/.well-known/oauth-app-manifest.schema.json",
    schemaVersion: "1.0.0",
    distribution: "private",
    display: {
      description: "Mention or delegate issues to mayaboti as a native Linear agent.",
      iconUrl: "https://raw.githubusercontent.com/HKUDS/mayaboti/main/images/mayaboti_logo.png",
    },
    developer: { name: "mayaboti" },
    oauth: {
      client_name: "mayaboti Agent",
      client_uri: "https://github.com/HKUDS/mayaboti",
      redirect_uris: [`${publicBaseUrl}${callbackPath}`],
      grant_types: ["authorization_code"],
    },
    webhook: {
      enabled: true,
      url: `${publicBaseUrl}${webhookPath}`,
      resourceTypes: [
        "AgentSessionEvent",
        "PermissionChange",
        "OAuthAuthorization",
      ],
    },
  };
  return `https://linear.app/settings/api/applications/new?${new URLSearchParams({
    manifest: JSON.stringify(manifest),
  })}`;
}
