import "../styles/default.css"; 
import "../styles/notification.css"

 function NewAccountNotification({ notification, onApprove, onReject }) {
  return (
    <div className="notification-item">
      <div className="notification-header">
        <span className="notification-sender">{notification.sender}</span>
        <span className="notification-date">{new Date(notification.date).toLocaleString()}</span>
      </div>
      <div className="notification-body">{notification.body}</div>
      <div className="notification-actions">
        <button className="btn-approve" onClick={() => onApprove(notification)}>Approve</button>
        <button className="btn-reject" onClick={() => onReject(notification)}>Reject</button>
      </div>
    </div>
  );
}

export default function NotificationItem({notification, onApprove, onReject }) {
  switch (notification.type) {
    case "a":
      return <NewAccountNotification notification={notification} onApprove={onApprove} onReject={onReject} />;
    default:
      return (
        <div className="notification-item">
          <div className="notification-header">
            <span>{notification.sender}</span>
            <span>{new Date(notification.date).toLocaleString()}</span>
          </div>
          <div>{notification.body}</div>
        </div>
      );
  }
}