export function Skeleton({ width, height = 18, style }: { width?: string | number; height?: number; style?: React.CSSProperties }) {
  return <div className="skeleton" style={{ width: width ?? '100%', height, ...style }} />;
}
