import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';

export default function HeroCarousel({ slides = [] }) {
  const [index, setIndex] = useState(0);
  const count = slides.length;

  const goTo = useCallback((i) => {
    if (!count) return;
    setIndex(((i % count) + count) % count);
  }, [count]);

  useEffect(() => {
    if (count < 2) return undefined;
    const timer = window.setInterval(() => goTo(index + 1), 6000);
    return () => window.clearInterval(timer);
  }, [count, index, goTo]);

  if (!count) return null;

  const slide = slides[index];

  return (
    <section className="hero-carousel" aria-label="Featured highlights">
      <div className="hero-carousel__track">
        {slides.map((item, i) => (
          <article
            key={item.id}
            className={`hero-card ${i === index ? 'is-active' : ''}`}
            style={{ '--hero-accent': item.accent || '#3b82f6' }}
            aria-hidden={i !== index}
          >
            <div className="hero-card__content">
              <p className="hero-card__text">{item.text}</p>
              {item.to ? (
                <Link to={item.to} className="hero-card__cta">
                  {item.cta}
                </Link>
              ) : (
                <span className="hero-card__cta hero-card__cta--static">{item.cta}</span>
              )}
            </div>
            <div className="hero-card__art" aria-hidden="true">
              <span className="hero-card__emoji">{item.emoji}</span>
            </div>
          </article>
        ))}
      </div>
      <div className="hero-carousel__dots" role="tablist" aria-label="Carousel pages">
        {slides.map((item, i) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={i === index}
            aria-label={`Slide ${i + 1}`}
            className={`hero-dot ${i === index ? 'is-active' : ''}`}
            onClick={() => goTo(i)}
          />
        ))}
      </div>
    </section>
  );
}
