type ConnectionCardProps = {
    title: string;
    description: string;
    icon: React.ReactNode;
    badge?: string;
    supported?: string[];
    ctaLabel: string;
    disabled?: boolean;
    accent: "green" | "blue" | "purple" | "pink" | "yellow";
    onAction?: () => void;
};

const getAccentClasses = (accent: "green" | "blue" | "purple" | "pink" | "yellow") => {
    const colorMap = {
        green: {
            bg: "bg-emerald-500/10",
            text: "text-emerald-400",
            border: "border-emerald-500/20",
            hover: "hover:border-emerald-500/40",
            buttonBgColor: "#059669",
            buttonHoverColor: "#047857",
            shadowColor: "rgba(16, 185, 129, 0.3)",
        },
        blue: {
            bg: "bg-blue-500/10",
            text: "text-blue-400",
            border: "border-blue-500/20",
            hover: "hover:border-blue-500/40",
            buttonBgColor: "#2563eb",
            buttonHoverColor: "#1d4ed8",
            shadowColor: "rgba(37, 99, 235, 0.3)",
        },
        purple: {
            bg: "bg-purple-500/10",
            text: "text-purple-400",
            border: "border-purple-500/20",
            hover: "hover:border-purple-500/40",
            buttonBgColor: "#9333ea",
            buttonHoverColor: "#7e22ce",
            shadowColor: "rgba(147, 51, 234, 0.3)",
        },
        pink: {
            bg: "bg-pink-500/10",
            text: "text-pink-400",
            border: "border-pink-500/20",
            hover: "hover:border-pink-500/40",
            buttonBgColor: "#ec4899",
            buttonHoverColor: "#db2777",
            shadowColor: "rgba(236, 72, 153, 0.3)",
        },
        yellow: {
            bg: "bg-yellow-500/10",
            text: "text-yellow-400",
            border: "border-yellow-500/20",
            hover: "hover:border-yellow-500/40",
            buttonBgColor: "#eab308",
            buttonHoverColor: "#ca8a04",
            shadowColor: "rgba(234, 179, 8, 0.3)",
        },
    };
    return colorMap[accent];
};

export function ConnectionCard({
    title,
    description,
    icon,
    badge,
    supported,
    ctaLabel,
    disabled = false,
    accent,
    onAction
}: ConnectionCardProps) {
    const colors = getAccentClasses(accent);

    return (
        <div
            className={`
        relative rounded-2xl flex flex-col items-start p-4 w-full
        bg-linear-to-br from-slate-900/80 via-slate-950/80 to-slate-900/80
        border border-slate-800/60 ${colors.border}
        transition-all duration-200 
        ${!disabled && `${colors.hover} hover:shadow-lg`}
        ${disabled && "opacity-60 cursor-not-allowed"}
      `}
        >
            {/* Badge */}
            {/* {badge && (
                <span className={`absolute top-4 right-4 text-xs px-2 py-1 rounded-full
          bg-white/10 text-slate-300 font-medium`}>
                    {badge}
                </span>
            )} */}

            {/* Icon */}
            <div
                className={`
          w-10 h-10 flex items-center justify-center rounded-lg mb-4
          ${colors.bg} ${colors.text}
        `}
            >
                {icon}
            </div>

            {/* Content */}
            <h3 className="text-white font-semibold text-base mb-1">
                {title}
            </h3>

            <p className="text-slate-400 text-sm mb-4">
                {description}
            </p>

            {/* Supported */}
            {supported && (
                <div className="flex flex-wrap gap-2 mb-4">
                    {supported.map((item) => (
                        <span
                            key={item}
                            className={`text-xs px-2 py-1 rounded-md
                bg-slate-800/50 text-slate-300`}
                        >
                            {item}
                        </span>
                    ))}
                </div>
            )}

            {/* CTA */}
            {!disabled ? (
                <button
                    className={`
              w-full rounded-lg py-2 px-3 text-sm font-medium text-white
              transition-all duration-300 transform hover:scale-105 active:scale-95
            `}
                    style={{
                        backgroundColor: colors.buttonBgColor,
                        boxShadow: `0 10px 25px -5px ${colors.shadowColor}`,
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = colors.buttonHoverColor;
                        e.currentTarget.style.boxShadow = `0 20px 35px -5px ${colors.shadowColor}`;
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = colors.buttonBgColor;
                        e.currentTarget.style.boxShadow = `0 10px 25px -5px ${colors.shadowColor}`;
                    }}
                    onClick={() => onAction?.()}
                >
                    {ctaLabel}
                </button>
            ) : (
                <button
                    disabled
                    className="w-full rounded-lg py-2 px-3 text-sm font-medium text-white
              bg-slate-700/50 text-slate-500 cursor-not-allowed
            "
                >
                    {ctaLabel}
                </button>
            )}
        </div>
    );
}
