type Props = {
  youtubeId: string;
  title: string;
};

export function ContentViewer({ youtubeId, title }: Props) {
  return (
    <div className="viewer">
      <h2>{title}</h2>
      <div className="viewer-frame">
        <iframe
          title={title}
          src={`https://www.youtube.com/embed/${youtubeId}?rel=0`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  );
}
