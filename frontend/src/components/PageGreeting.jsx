function getTimeGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

function formatHeaderDate(date = new Date()) {
  return date.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
}

export default function PageGreeting({ name, subtitle, className = '' }) {
  const displayName = name?.split(' ')[0] || 'there';
  return (
    <header className={`page-greeting ${className}`.trim()}>
      <span className="page-greeting__date">{formatHeaderDate()}</span>
      <h1 className="page-greeting__title">
        {getTimeGreeting()}, <span>{displayName}</span>
      </h1>
      {subtitle && <p className="page-greeting__subtitle">{subtitle}</p>}
    </header>
  );
}
