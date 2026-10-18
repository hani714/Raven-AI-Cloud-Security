import { Star } from 'lucide-react';

const testimonials = [
  {
    quote: "AWS Pentest Toolkit transformed our security posture. We identified critical misconfigurations within minutes that would have taken weeks to find manually.",
    author: 'Sarah Chen',
    role: 'CISO',
    company: 'TechScale Inc.',
    avatar: 'SC',
  },
  {
    quote: "The automated remediation steps saved our team countless hours. It's like having a senior security engineer on call 24/7.",
    author: 'Marcus Thompson',
    role: 'Head of DevSecOps',
    company: 'CloudFirst Solutions',
    avatar: 'MT',
  },
  {
    quote: "Finally, a pentest tool that understands AWS inside out. The IAM analysis alone has prevented potential breaches for us.",
    author: 'Emily Rodriguez',
    role: 'Security Architect',
    company: 'FinSecure Bank',
    avatar: 'ER',
  },
  {
    quote: "We passed our SOC 2 audit on the first attempt thanks to the comprehensive compliance reporting. Highly recommended.",
    author: 'David Kim',
    role: 'VP of Engineering',
    company: 'DataFlow Systems',
    avatar: 'DK',
  },
];

const Testimonials = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card/30 to-background pointer-events-none" />
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <span className="text-accent-landing text-sm font-semibold tracking-wider uppercase">Testimonials</span>
          <h2 className="text-3xl md:text-4xl font-bold mt-4">
            Trusted by Security Teams Worldwide
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {testimonials.map((testimonial, _) => (
            <div
              key={testimonial.author}
              className="glass-card rounded-2xl p-6 transition-all duration-300 hover:border-accent-landing/50 group"
            >
              {/* Stars */}
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-accent-landing text-accent-landing" />
                ))}
              </div>

              <blockquote className="text-foreground mb-6">
                "{testimonial.quote}"
              </blockquote>

              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-accent-landing/20 border border-accent-landing/30 flex items-center justify-center text-accent-landing font-semibold">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold">{testimonial.author}</div>
                  <div className="text-sm text-muted-foreground-landing">
                    {testimonial.role}, {testimonial.company}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
