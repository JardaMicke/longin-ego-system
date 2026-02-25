import { formatBytes } from "../../utils/contextUtils";

export const ContextItemList = ({ items, onRemove, onRetry }) => (
  <div className="context-list">
    {items.length === 0 ? (
      <div className="context-empty">Zatím žádný kontext.</div>
    ) : null}
    {items.map((item) => (
      <div key={item.id} className={`context-item ${item.status}`}>
        <div className="context-item-header">
          <div>
            <div className="context-item-title">{item.title}</div>
            <div className="context-item-meta">
              <span>{item.type}</span>
              {item.size ? <span>{formatBytes(item.size)}</span> : null}
              <span>{item.status}</span>
            </div>
          </div>
          <div className="context-item-actions">
            {item.status === "failed" ? (
              <button
                type="button"
                className="ghost-button"
                onClick={() => onRetry(item.id)}
              >
                Zkusit znovu
              </button>
            ) : null}
            <button type="button" className="ghost-button" onClick={() => onRemove(item.id)}>
              Odebrat
            </button>
          </div>
        </div>
        {item.preview ? <div className="context-preview">{item.preview}</div> : null}
        {item.error ? <div className="context-error">{item.error}</div> : null}
        {item.progress > 0 && item.progress < 100 ? (
          <div className="context-progress">
            <div className="context-progress-bar" style={{ width: `${item.progress}%` }} />
          </div>
        ) : null}
      </div>
    ))}
  </div>
);
