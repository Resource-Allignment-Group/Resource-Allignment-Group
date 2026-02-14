//For viewing equipment images with navigation between images
import { useEffect } from "react";

function ImageViewerModal({ isOpen, onClose, images, currentIndex, onIndexChange }) {
	useEffect(() => {
		const handleKeyDown = (e) => {
			if (!isOpen) return;
			if (e.key === "Escape") onClose();
			if (e.key === "ArrowLeft") onIndexChange(Math.max(0, currentIndex - 1));
			if (e.key === "ArrowRight") onIndexChange(Math.min(images.length - 1, currentIndex + 1));
		};
		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [isOpen, currentIndex, images.length, onClose, onIndexChange]);

	if (!isOpen || !images?.length) return null;

	const currentImage = images[currentIndex];
	const canGoLeft = currentIndex > 0;
	const canGoRight = currentIndex < images.length - 1;

	return (
		<div className="image-viewer-overlay" onClick={onClose}>
			<div className="image-viewer-modal" onClick={(e) => e.stopPropagation()}>
				<button
					className="image-viewer-close"
					onClick={onClose}
					aria-label="Close"
				>
					×
				</button>
				{canGoLeft && (
					<button
						className="image-viewer-nav image-viewer-nav-left"
						onClick={(e) => {
							e.stopPropagation();
							onIndexChange(currentIndex - 1);
						}}
						aria-label="Previous image"
					>
						←
					</button>
				)}
				<div className="image-viewer-content">
					<img src={currentImage} alt="" />
				</div>
				{canGoRight && (
					<button
						className="image-viewer-nav image-viewer-nav-right"
						onClick={(e) => {
							e.stopPropagation();
							onIndexChange(currentIndex + 1);
						}}
						aria-label="Next image"
					>
						→
					</button>
				)}
				{images.length > 1 && (
					<div className="image-viewer-counter">
						{currentIndex + 1} / {images.length}
					</div>
				)}
			</div>
		</div>
	);
}

export default ImageViewerModal;
