First browser attempt failed at app-ready with HTTP 404 because the temporary
server was started at the repository root instead of site/. No application
defect or passed regression was inferred. The server root and test URL were
corrected before rerunning. Application HTML was not changed to fix this server
setup issue. A later, separate UI change qualified historical geometry messages;
the final browser checks were rerun after that change.

First Blender invocation lacked __file__ in the MCP execution namespace and
failed before import/scene changes. Retried with an explicit script namespace;
the audit then passed and restored the original scene.
