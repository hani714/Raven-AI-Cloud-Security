import { Shield, Database, Server, Zap, Eye, FileText } from 'lucide-react';

const features = [
  {
    icon: Shield,
    title: 'IAM Misconfiguration Detection',
    description: 'Identify overly permissive policies, unused credentials, and privilege escalation paths.',
    color: 'hsl(var(--secondary))',
  },
  {
    icon: Database,
    title: 'S3 Bucket Exposure Scan',
    description: 'Detect public buckets, misconfigured ACLs, and sensitive data exposure risks.',
    color: 'hsl(var(--severity-high))',
  },
  {
    icon: Server,
    title: 'EC2 Security Posture Review',
    description: 'Analyze security groups, network configurations, and instance metadata vulnerabilities.',
    color: 'hsl(var(--accent))',
  },
  {
    icon: Zap,
    title: 'Lambda & API Gateway Checks',
    description: 'Review function permissions, API authentication, and serverless security best practices.',
    color: 'hsl(var(--primary))',
  },
  {
    icon: Eye,
    title: 'Real-time Threat Insights',
    description: 'Monitor for active threats, anomalous behavior, and potential security incidents.',
    color: 'hsl(280 80% 65%)',
  },
  {
    icon: FileText,
    title: 'Exportable PDF Reports',
    description: 'Generate comprehensive pentest reports ready for compliance audits and stakeholders.',
    color: 'hsl(180 60% 55%)',
  },
];

const FeaturesGrid = () => {
  return (
    <section id="features" className="py-24 relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <span className="font-mono text-primary text-xs font-semibold tracking-[0.3em] uppercase">// Features</span>
          <h2 className="text-3xl md:text-4xl font-bold mt-4 font-display">
            Enterprise-Grade Security Testing
          </h2>
          <p className="text-muted-foreground-landing mt-4 max-w-2xl mx-auto">
            Comprehensive vulnerability detection across your entire AWS infrastructure
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group relative glass-card rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1"
              style={
                {
                  // dynamic crimson border on hover via inline var
                  ['--feature-color' as any]: feature.color,
                }
              }
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLDivElement).style.borderColor = `${feature.color}`;
                (e.currentTarget as HTMLDivElement).style.boxShadow = `0 0 32px -10px ${feature.color}`;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLDivElement).style.borderColor = '';
                (e.currentTarget as HTMLDivElement).style.boxShadow = '';
              }}
            >
              <div className="relative z-10">
                <div
                  className="mb-4 p-3 rounded-xl w-fit transition-colors duration-300"
                  style={{
                    background: `${feature.color.replace(')', ' / 0.1)')}`,
                    border: `1px solid ${feature.color.replace(')', ' / 0.3)')}`,
                  }}
                >
                  <feature.icon className="h-6 w-6" style={{ color: feature.color }} />
                </div>

                <h3
                  className="text-lg font-semibold mb-2 font-display transition-colors duration-300"
                  style={{ color: 'hsl(var(--foreground))' }}
                >
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground-landing">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesGrid;
