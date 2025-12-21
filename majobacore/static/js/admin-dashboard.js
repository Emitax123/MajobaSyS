document.addEventListener('DOMContentLoaded', function () {
      const successAlert = document.getElementById('success-alert')
      if (successAlert) {
        setTimeout(function () {
          successAlert.style.transition = 'opacity 0.5s ease-out'
          successAlert.style.opacity = '0'
    
          // Remover completamente el elemento después de la transición
          setTimeout(function () {
            successAlert.remove()
          }, 500)
        }, 3000)
      }
    })