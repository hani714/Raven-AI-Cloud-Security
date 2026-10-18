import { CheckCircle, Shield, Lock, FileCheck } from 'lucide-react';

const certifications = [
  { name: 'CIS Benchmarks', description: 'Center for Internet Security' },
  { name: 'NIST Framework', description: 'National Institute of Standards' },
  { name: 'OWASP Cloud', description: 'Cloud Security Guidelines' },
  { name: 'AWS Best Practices', description: 'Well-Architected Framework' },
];

const SecurityCompliance = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-card via-background to-card pointer-events-none" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8">
            <div>
              <span className="font-mono text-primary text-xs font-semibold tracking-[0.3em] uppercase">// Security & Compliance</span>
              <h2 className="text-3xl md:text-4xl font-bold mt-4 font-display">
                Built for Enterprise Security Standards
              </h2>
              <p className="text-muted-foreground-landing mt-4">
                Our platform is designed to meet the most stringent security and compliance requirements, ensuring your AWS infrastructure adheres to industry best practices.
              </p>
            </div>

            <div className="space-y-4">
              {[
                'Automated compliance checking against major frameworks',
                'Continuous monitoring and real-time alerting',
                'Detailed audit trails for compliance reporting',
                'Zero data retention policy available',
              ].map((item, index) => (
                <div key={index} className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-accent flex-shrink-0" />
                  <span className="text-muted-foreground-landing">{item}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {certifications.map((cert, index) => (
              <div
                key={cert.name}
                className="glass-card rounded-xl p-6 text-center transition-all duration-500 hover:border-primary/40 hover:-translate-y-1 hover:shadow-[0_0_24px_-8px_hsl(var(--primary)/0.4)]"
                style={{
                  animation: `fadeUp 0.6s ease-out ${index * 0.15}s both`,
                }}
              >
                <div className="mx-auto mb-4 p-3 rounded-xl bg-primary/10 border border-primary/20 w-fit">
                  {index === 0 && <Shield className="h-6 w-6 text-primary" />}
                  {index === 1 && <Lock className="h-6 w-6 text-secondary" />}
                  {index === 2 && <FileCheck className="h-6 w-6 text-accent" />}
                  {index === 3 && <CheckCircle className="h-6 w-6 text-[hsl(var(--severity-high))]" />}
                </div>
                <h3 className="font-semibold mb-1 font-display">{cert.name}</h3>
                <p className="text-xs text-muted-foreground-landing font-mono uppercase tracking-wider">{cert.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default SecurityCompliance;
