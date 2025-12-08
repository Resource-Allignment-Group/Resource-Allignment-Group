import "../styles/default.css"; 
import "../styles/notification.css"

import { useState } from "react";

function NewAccountNotification({ notification, onApprove, onReject }) {
  const [status, setStatus] = useState(null); 

  const handleApproveClick = () => {
    setStatus("approved");
    onApprove(notification);
  };

  const handleRejectClick = () => {
    setStatus("rejected");
    onReject(notification);
  };

  return (
    <div className="notification-item">
      <div className="notification-header">
        <span className="notification-sender">{notification.sender_username}</span>
        <span className="notification-date">{new Date(notification.date).toLocaleString()}</span>
      </div>

      <div className="notification-body">{notification.body}</div>

      <div className="notification-actions">
        {status === null && (
          <>
            <button className="btn-approve" onClick={handleApproveClick}>Approve</button>
            <button className="btn-reject" onClick={handleRejectClick}>Reject</button>
          </>
        )}

        {status === "approved" && (
          <p className="approved-text">Approved</p>
        )}

        {status === "rejected" && (
          <p className="rejected-text">Rejected</p>
        )}
      </div>
    </div>
  );
}

export default function NotificationItem({notification, onApprove, onReject }) {
  switch (notification.type) {
    case "a": //add oher cases hear for each type of notification
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