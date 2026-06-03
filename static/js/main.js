document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(el) {
        return new bootstrap.Tooltip(el);
    });

    const autoHideAlerts = document.querySelectorAll('.alert-dismissible');
    autoHideAlerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 8000);
    });

    const riskBadges = document.querySelectorAll('.badge');
    riskBadges.forEach(function(badge) {
        const text = badge.textContent.trim();
        if (text === 'Low' || (parseFloat(text) <= 25 && !isNaN(parseFloat(text)))) {
            badge.classList.add('bg-success');
        } else if (text === 'Medium' || (parseFloat(text) <= 50 && !isNaN(parseFloat(text)))) {
            badge.classList.add('bg-warning', 'text-dark');
        } else if (text === 'High' || (parseFloat(text) <= 75 && !isNaN(parseFloat(text)))) {
            badge.classList.add('bg-orange');
        } else if (text === 'Critical' || (parseFloat(text) > 75 && !isNaN(parseFloat(text)))) {
            badge.classList.add('bg-danger');
        }
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
