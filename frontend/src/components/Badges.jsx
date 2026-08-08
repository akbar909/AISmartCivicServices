export function StatusBadge({ status }) {
  const variants = {
    'Open': 'badge-open',
    'Assigned': 'badge-assigned',
    'In Progress': 'badge-progress',
    'Resolved': 'badge-resolved',
  };
  return (
    <span className={variants[status] || 'badge-open'}>
      {status}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  const variants = {
    'Critical': 'badge-critical',
    'High': 'badge-high',
    'Medium': 'badge-medium',
    'Low': 'badge-low',
  };
  return (
    <span className={variants[priority] || 'badge-medium'}>
      {priority}
    </span>
  );
}
