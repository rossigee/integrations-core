docker exec `docker ps | grep k8s_agent_datadog | rev | cut -d ' ' -f 1 | rev` tail -f /var/log/datadog/agent.log
