export const ContextLogs = ({ logs }) => (
  <div className="context-logs">
    <div className="context-logs-title">Logy</div>
    <div className="context-logs-body">
      {logs.length === 0 ? <div className="context-empty">Bez logů.</div> : null}
      {logs.map((log) => (
        <div key={log.id} className={`context-log ${log.level}`}>
          <div className="context-log-line">
            <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
            <span>{log.message}</span>
          </div>
        </div>
      ))}
    </div>
  </div>
);
