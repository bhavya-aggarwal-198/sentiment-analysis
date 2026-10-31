document.addEventListener("DOMContentLoaded", () => {
    const modelOptions = document.querySelectorAll(".model-option");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const aboutDialog = document.querySelector("#about-dialog");
    const aboutTrigger = document.querySelector(".about-trigger");
    const aboutClose = document.querySelector("[data-close-about]");

    aboutTrigger.addEventListener("click", () => aboutDialog.showModal());
    aboutClose.addEventListener("click", () => aboutDialog.close());
    aboutDialog.addEventListener("click", (event) => {
        if (event.target === aboutDialog) {
            aboutDialog.close();
        }
    });

    modelOptions.forEach((option) => {
        const input = option.querySelector('input[type="radio"]');
        input.addEventListener("change", () => {
            modelOptions.forEach((item) => item.classList.remove("is-selected"));
            option.classList.add("is-selected");
        });
    });

    if (reducedMotion || typeof window.gsap === "undefined") {
        return;
    }

    const gsap = window.gsap;
    const intro = document.querySelector(".intro");
    const header = document.querySelector(".site-header");
    const panels = document.querySelectorAll(".analyzer-card, .result-card");
    const timeline = gsap.timeline({ defaults: { ease: "power3.out" } });

    timeline.from(header, { y: -16, opacity: 0, duration: 0.65 });
    timeline.from(intro.querySelectorAll(".eyebrow, h1, .intro-copy"), {
        y: 22,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
    }, "-=0.35");
    timeline.from(panels, { y: 24, opacity: 0, duration: 0.7, stagger: 0.14 }, "-=0.35");

    const meterFills = document.querySelectorAll(".meter-fill");
    if (meterFills.length) {
        gsap.fromTo(
            meterFills,
            { width: "0%" },
            {
                width: (index, element) => `${element.dataset.score}%`,
                duration: 1.1,
                ease: "power2.out",
                stagger: 0.12,
                delay: 0.6,
            },	3578031

        );
    }

    const orbit = document.querySelector(".result-orbit");
    if (orbit) {
        gsap.to(orbit.querySelector(".orbit-ring--one"), {
            rotation: 360,
            duration: 18,
            ease: "none",
            repeat: -1,
        });
        gsap.to(orbit.querySelector(".orbit-ring--two"), {
            rotation: -360,
            duration: 28,
            ease: "none",
            repeat: -1,
        });
    }
});