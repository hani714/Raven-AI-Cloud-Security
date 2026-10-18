import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/ui/accordion';

const faqs = [
  {
    question: 'How does AWS Pentest Toolkit access my AWS account?',
    answer: 'We use IAM roles with read-only permissions to access your AWS account. You maintain full control over what resources we can scan, and no write operations are ever performed on your infrastructure.',
  },
  {
    question: 'What AWS services are covered in the security scan?',
    answer: 'Our platform covers all major AWS services including IAM, S3, EC2, RDS, Lambda, API Gateway, CloudFront, VPC, EKS, ECS, and more. We continuously add support for new services as they become available.',
  },
  {
    question: 'How long does a typical security scan take?',
    answer: 'Scan duration depends on the size of your infrastructure. Most scans complete within 15-30 minutes for small to medium accounts. Enterprise accounts with thousands of resources may take up to 2 hours.',
  },
  {
    question: 'Is my data stored securely during scans?',
    answer: 'All scan data is encrypted at rest and in transit. We follow a zero-trust architecture and offer data retention policies including immediate deletion after reports are generated.',
  },
  {
    question: 'Can I integrate with my existing security tools?',
    answer: 'Yes, we offer integrations with popular SIEM tools, ticketing systems like Jira, and CI/CD pipelines. Our API allows for custom integrations with any platform.',
  },
  {
    question: 'Do you offer custom compliance frameworks?',
    answer: 'Enterprise customers can define custom compliance frameworks tailored to their specific regulatory requirements. We also support major frameworks like SOC 2, HIPAA, PCI-DSS, and GDPR out of the box.',
  },
];

const FAQSection = () => {
  return (
    <section id="faq" className="py-24 relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <span className="font-mono text-primary text-xs font-semibold tracking-[0.3em] uppercase">// FAQ</span>
          <h2 className="text-3xl md:text-4xl font-bold mt-4 font-display">
            Frequently Asked Questions
          </h2>
        </div>

        <div className="max-w-3xl mx-auto">
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="glass-card rounded-xl border-border-landing/50 px-6 data-[state=open]:border-primary/40 data-[state=open]:shadow-[0_0_24px_-12px_hsl(var(--primary)/0.4)]"
              >
                <AccordionTrigger className="text-left hover:text-primary hover:no-underline py-6 text-base font-medium [&_svg]:text-primary [&[data-state=open]_svg]:rotate-180">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground-landing pb-6">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  );
};

export default FAQSection;
