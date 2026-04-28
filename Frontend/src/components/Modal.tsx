import React, { useEffect, ReactNode } from "react";

interface ModalProps {
    visible: boolean;
    handleModalToggle: () => void;
    children: ReactNode;
    position?: Record<string, string | number>;
    containerClassName?: string;
}

const Modal = ({
    visible,
    handleModalToggle,
    children,
    position,
    containerClassName,
}: ModalProps) => {
    const handleClickOutside = (event: React.MouseEvent<HTMLDivElement>) => {
        if (event.target === event.currentTarget) {
            handleModalToggle();
        }
    };

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                handleModalToggle();
            }
        };

        if (visible) {
            document.addEventListener("keydown", handleKeyDown);
            return () => {
                document.removeEventListener("keydown", handleKeyDown);
            };
        }
    }, [visible, handleModalToggle]);

    if (!visible) return null;

    const containerClass = containerClassName
        ? containerClassName
        : position
            ? "fixed inset-0 bg-black bg-opacity-30 backdrop-blur-sm z-50 w-screen h-screen"
            : "fixed inset-0 bg-black bg-opacity-30 backdrop-blur-sm grid place-content-center z-50 w-screen h-screen";

    const childrenStyle = position ? { position: "absolute", ...position } : {};

    return (
        <div className={containerClass} onClick={handleClickOutside}>
            <div style={childrenStyle}>{children}</div>
        </div>
    );
};

export default Modal;
