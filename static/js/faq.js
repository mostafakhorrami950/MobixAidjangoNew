document.addEventListener('DOMContentLoaded', function() {
  const faqItems = document.querySelectorAll('.faq-item h4');
  
  faqItems.forEach(item => {
    item.addEventListener('click', function() {
      const faqItem = this.parentElement;
      const answer = faqItem.querySelector('p');
      const isActive = faqItem.classList.contains('active');
      
      // Close all other FAQ items
      document.querySelectorAll('.faq-item').forEach(otherItem => {
        if (otherItem !== faqItem) {
          otherItem.classList.remove('active');
          const otherAnswer = otherItem.querySelector('p');
          if (otherAnswer) otherAnswer.classList.remove('active');
          const otherTitle = otherItem.querySelector('h4');
          if (otherTitle) otherTitle.classList.remove('active');
        }
      });
      
      // Toggle current FAQ item
      if (!isActive) {
        faqItem.classList.add('active');
        answer.classList.add('active');
        this.classList.add('active');
        // Add slide down animation
        answer.style.maxHeight = answer.scrollHeight + 'px';
      } else {
        faqItem.classList.remove('active');
        answer.classList.remove('active');
        this.classList.remove('active');
        answer.style.maxHeight = '0';
      }
    });
  });

  // Optional: Open first FAQ item by default
  if (faqItems.length > 0) {
    faqItems[0].click();
  }
});