export const ContextActionModal = ({ title, onClose, children }) => (
  <div className="context-modal-backdrop" role="dialog" aria-modal="true">
    <div className="context-modal">
      <div className="context-modal-header">
        <div className="context-modal-title">{title}</div>
        <button type="button" className="ghost-button" onClick={onClose} aria-label="Zavřít">
          Zavřít
        </button>
      </div>
      <div className="context-modal-body">{children}</div>
    </div>
  </div>
);
