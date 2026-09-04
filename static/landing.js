const heroObject = document.querySelector('#heroObject')
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

if (heroObject && !reducedMotion) {
  heroObject.addEventListener('pointermove', (event) => {
    const bounds = heroObject.getBoundingClientRect()
    const x = (event.clientX - bounds.left) / bounds.width - 0.5
    const y = (event.clientY - bounds.top) / bounds.height - 0.5
    heroObject.style.setProperty('--tilt-x', `${y * -7}deg`)
    heroObject.style.setProperty('--tilt-y', `${x * 9}deg`)
    heroObject.style.setProperty('--shift-x', `${x * 10}px`)
    heroObject.style.setProperty('--shift-y', `${y * 10}px`)
  })
  heroObject.addEventListener('pointerleave', () => {
    heroObject.style.setProperty('--tilt-x', '0deg')
    heroObject.style.setProperty('--tilt-y', '0deg')
    heroObject.style.setProperty('--shift-x', '0px')
    heroObject.style.setProperty('--shift-y', '0px')
  })
}

const revealItems = document.querySelectorAll('.reveal')
if ('IntersectionObserver' in window && !reducedMotion) {
  const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible')
      observer.unobserve(entry.target)
    }
  }), { threshold: 0.15 })
  revealItems.forEach((item) => observer.observe(item))
} else revealItems.forEach((item) => item.classList.add('is-visible'))
