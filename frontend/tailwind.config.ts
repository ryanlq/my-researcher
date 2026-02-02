import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: ["class"],
    content: [
        "./pages/**/*.{ts,tsx}",
        "./components/**/*.{ts,tsx}",
        "./app/**/*.{ts,tsx}",
        "./src/**/*.{ts,tsx}",
    ],
    prefix: "",
    theme: {
        container: {
            center: true,
            padding: "2rem",
            screens: {
                "2xl": "1400px",
            },
        },
        extend: {
            colors: {
                border: "hsl(var(--border))",
                input: "hsl(var(--input))",
                ring: "hsl(var(--ring))",
                background: "hsl(var(--background))",
                foreground: "hsl(var(--foreground))",
                primary: {
                    DEFAULT: "hsl(var(--primary))",
                    foreground: "hsl(var(--primary-foreground))",
                },
                secondary: {
                    DEFAULT: "hsl(var(--secondary))",
                    foreground: "hsl(var(--secondary-foreground))",
                },
                destructive: {
                    DEFAULT: "hsl(var(--destructive))",
                    foreground: "hsl(var(--destructive-foreground))",
                },
                muted: {
                    DEFAULT: "hsl(var(--muted))",
                    foreground: "hsl(var(--muted-foreground))",
                },
                accent: {
                    DEFAULT: "hsl(var(--accent))",
                    foreground: "hsl(var(--accent-foreground))",
                },
                popover: {
                    DEFAULT: "hsl(var(--popover))",
                    foreground: "hsl(var(--popover-foreground))",
                },
                card: {
                    DEFAULT: "hsl(var(--card))",
                    foreground: "hsl(var(--card-foreground))",
                },
                sidebar: {
                    DEFAULT: "hsl(var(--sidebar-background))",
                    foreground: "hsl(var(--sidebar-foreground))",
                    primary: "hsl(var(--sidebar-primary))",
                    "primary-foreground":
                        "hsl(var(--sidebar-primary-foreground))",
                    accent: "hsl(var(--sidebar-accent))",
                    "accent-foreground":
                        "hsl(var(--sidebar-accent-foreground))",
                    border: "hsl(var(--sidebar-border))",
                    ring: "hsl(var(--sidebar-ring))",
                },
            },
            borderRadius: {
                lg: "var(--radius)",
                md: "calc(var(--radius) - 2px)",
                sm: "calc(var(--radius) - 4px)",
            },
            keyframes: {
                // 默认 Tailwind 动画
                spin: {
                    from: {
                        transform: "rotate(0deg)",
                    },
                    to: {
                        transform: "rotate(360deg)",
                    },
                },
                ping: {
                    "75%, 100%": {
                        transform: "scale(2)",
                        opacity: "0",
                    },
                },
                pulse: {
                    "0%, 100%": {
                        opacity: "1",
                    },
                    "50%": {
                        opacity: "0.5",
                    },
                },
                bounce: {
                    "0%, 100%": {
                        transform: "translateY(-25%)",
                        animationTimingFunction: "cubic-bezier(0.8, 0, 1, 1)",
                    },
                    "50%": {
                        transform: "translateY(0)",
                        animationTimingFunction: "cubic-bezier(0, 0, 0.2, 1)",
                    },
                },
                // Accordion 动画
                "accordion-down": {
                    from: {
                        height: "0",
                    },
                    to: {
                        height: "var(--radix-accordion-content-height)",
                    },
                },
                "accordion-up": {
                    from: {
                        height: "var(--radix-accordion-content-height)",
                    },
                    to: {
                        height: "0",
                    },
                },
                // 自定义 Loader 动画
                typing: {
                    "0%, 100%": {
                        transform: "translateY(0)",
                        opacity: "0.5",
                    },
                    "50%": {
                        transform: "translateY(-2px)",
                        opacity: "1",
                    },
                },
                "loading-dots": {
                    "0%, 100%": {
                        opacity: "0",
                    },
                    "50%": {
                        opacity: "1",
                    },
                },
                wave: {
                    "0%, 100%": {
                        transform: "scaleY(1)",
                    },
                    "50%": {
                        transform: "scaleY(0.6)",
                    },
                },
                blink: {
                    "0%, 100%": {
                        opacity: "1",
                    },
                    "50%": {
                        opacity: "0",
                    },
                },
                "text-blink": {
                    "0%, 100%": {
                        color: "var(--primary)",
                    },
                    "50%": {
                        color: "var(--muted-foreground)",
                    },
                },
                "bounce-dots": {
                    "0%, 100%": {
                        transform: "scale(0.8)",
                        opacity: "0.5",
                    },
                    "50%": {
                        transform: "scale(1.2)",
                        opacity: "1",
                    },
                },
                "thin-pulse": {
                    "0%, 100%": {
                        transform: "scale(0.95)",
                        opacity: "0.8",
                    },
                    "50%": {
                        transform: "scale(1.05)",
                        opacity: "0.4",
                    },
                },
                "pulse-dot": {
                    "0%, 100%": {
                        transform: "scale(1)",
                        opacity: "0.8",
                    },
                    "50%": {
                        transform: "scale(1.5)",
                        opacity: "1",
                    },
                },
                "shimmer-text": {
                    "0%": {
                        backgroundPosition: "150% center",
                    },
                    "100%": {
                        backgroundPosition: "-150% center",
                    },
                },
                "wave-bars": {
                    "0%, 100%": {
                        transform: "scaleY(1)",
                        opacity: "0.5",
                    },
                    "50%": {
                        transform: "scaleY(0.6)",
                        opacity: "1",
                    },
                },
                shimmer: {
                    "0%": {
                        backgroundPosition: "200% 50%",
                    },
                    "100%": {
                        backgroundPosition: "-200% 50%",
                    },
                },
                "spinner-fade": {
                    "0%": {
                        opacity: "0",
                    },
                    "100%": {
                        opacity: "1",
                    },
                },
            },
            animation: {
                // 默认 Tailwind 动画
                spin: "spin 1s linear infinite",
                ping: "ping 1s cubic-bezier(0, 0, 0.2, 1) infinite",
                pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                bounce: "bounce 1s infinite",
                // Accordion 动画
                "accordion-down": "accordion-down 0.2s ease-out",
                "accordion-up": "accordion-up 0.2s ease-out",
                // 自定义 Loader 动画
                typing: "typing 1s infinite",
                "loading-dots": "loading-dots 1.4s infinite",
                wave: "wave 1s ease-in-out infinite",
                blink: "blink 1s step-end infinite",
                "text-blink": "text-blink 2s ease-in-out infinite",
                "bounce-dots": "bounce-dots 1.4s ease-in-out infinite",
                "thin-pulse": "thin-pulse 1.5s ease-in-out infinite",
                "pulse-dot": "pulse-dot 1.2s ease-in-out infinite",
                "shimmer-text": "shimmer-text 4s infinite linear",
                "wave-bars": "wave-bars 1.2s ease-in-out infinite",
                shimmer: "shimmer 4s infinite linear",
                "spinner-fade": "spinner-fade 1.2s linear infinite",
            },
        },
    },
    plugins: [
        require("@tailwindcss/typography"),
        require("tailwindcss-animate"),
    ],
};

export default config;
