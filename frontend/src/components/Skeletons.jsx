export function CardSkeleton({ count = 3 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card p-6 space-y-3">
          <div className="skeleton h-4 w-3/4" />
          <div className="skeleton h-3 w-full" />
          <div className="skeleton h-3 w-5/6" />
          <div className="flex gap-2 mt-4">
            <div className="skeleton h-6 w-16 rounded-full" />
            <div className="skeleton h-6 w-20 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 card">
          <div className="skeleton h-4 w-1/4" />
          <div className="skeleton h-4 w-1/3" />
          <div className="skeleton h-6 w-16 rounded-full" />
          <div className="skeleton h-6 w-20 rounded-full" />
          <div className="skeleton h-4 w-24 ml-auto" />
        </div>
      ))}
    </div>
  );
}

export function StatSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card p-6">
          <div className="skeleton h-3 w-24 mb-3" />
          <div className="skeleton h-8 w-16 mb-2" />
          <div className="skeleton h-3 w-32" />
        </div>
      ))}
    </div>
  );
}
