import Navbar from '../components/landing/Navbar';
import HeroSection from '../components/landing/HeroSection';
import HowItWorks from '../components/landing/HowItWorks';
import FeaturesGrid from '../components/landing/FeaturesGrid';
import SecurityCompliance from '../components/landing/SecurityCompliance';
import PricingSection from '../components/landing/PricingSection';
// import Testimonials from '../components/landing/Testimonials';
import FAQSection from '../components/landing/FAQSection';
import Footer from '../components/landing/Footer';

const Landing = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <HeroSection />
        <HowItWorks />
        <FeaturesGrid />
        <SecurityCompliance />
        <PricingSection />
        {/* <Testimonials /> */}
        <FAQSection />
      </main>
      <Footer />
    </div>
  );
};

export default Landing;
