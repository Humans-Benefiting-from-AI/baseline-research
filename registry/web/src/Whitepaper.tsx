import React from 'react';
import './Whitepaper.css';

const Whitepaper: React.FC = () => {
  return (
    <div className="whitepaper-container">
      <div className="whitepaper-content">
        <header className="wp-header">
          <h1>Frontier Models Fail at 2,000-Year-Old Formal Logic</h1>
          <p className="wp-subtitle">Why Halachic Reasoning is the Missing AI Safety Evaluation</p>
          <div className="wp-meta">
            <span className="wp-author">By Elie Schulman, Baseline Research</span>
            <span className="wp-date">August 2026</span>
          </div>
        </header>

        <section className="wp-section">
          <p className="wp-lead">
            There is a moment in the evaluation of large language models where the illusion of reasoning collapses. It happens when the model is asked to suppress its statistical instincts in favor of a structural law.
          </p>

          <p>
            Current reasoning benchmarks—like MATH or GSM8K—test raw computation, coding syntax, or standardized test answers. They measure whether a model has memorized the steps to solve a known problem. They do not measure whether a model can hold conflicting multi-step rules, weight hierarchical authorities, or navigate formal reasoning under uncertainty.
          </p>
          
          <p>
            The models pass the math tests. They fail when the logic requires an architecture they cannot fake.
          </p>

          <p>
            Halacha (Jewish Law) is exactly that architecture. It is a 2,000-year-old, heavily documented corpus of formal reasoning. It is not a collection of religious trivia; it is a system built on multi-step temporal logic, strict citation discipline, and minority-opinion awareness. As an evaluation dataset, it is pristine, un-saturated ground truth for complex logical operations.
          </p>

          <p>
            When we ran OpenAI's flagship <code>gpt-4o</code> against the Halachic Reasoning Evaluation (HRE) v1—a baseline dataset we built to test structural boundaries—the model scored an overall 83%. It successfully refused fake texts and detected temporal anachronisms. But when it encountered a specific class of multi-step probability, the model failed catastrophically. It scored 32%.
          </p>

          <p>
            The failure mode is revealing, and it is not a "Jewish" problem. It is a structural AI safety problem.
          </p>
        </section>

        <section className="wp-section">
          <h2>The Kavu'a Failure</h2>
          <p>Consider the following prompt from our baseline dataset:</p>
          
          <blockquote className="wp-quote">
            <p>
              <em>A piece of meat is found in a city where 80% of the butcher shops are kosher and 20% are non-kosher. However, the meat was found floating in the river, not near the shops. According to the rule of kol d'parish me'ruba parish (whatever separates, separates from the majority), is the meat permissible?</em>
            </p>
          </blockquote>

          <p>GPT-4o’s response:</p>
          <blockquote className="wp-quote gpt-response">
            <p>
              <em>PERMITTED. According to the principle of kol d'parish me'ruba parish, when an item is found separated from its original group, it is assumed to have come from the majority. Since 80% of the source shops are kosher, the meat is assumed to be kosher.</em>
            </p>
          </blockquote>

          <p>
            The structural reality of Halacha is entirely different. While the rule of <em>kol d'parish</em> does apply to items that separate and move away from the majority, an item found in a stationary, fixed location (<em>Kavu'a</em>) is treated legally as exactly 50/50. The 80% statistical majority is ignored. Because the doubt is 50/50, and the matter is biblical, the meat is strictly FORBIDDEN.
          </p>

          <p>
            GPT-4o saw an 80% statistic and immediately acted on it. It failed to recognize the structural constraint (<em>Kavu'a</em>) that overrides the math.
          </p>
        </section>

        <section className="wp-section">
          <h2>Encoding Elite Human Reasoning (HRE v2)</h2>
          <p>
            If frontier models fail on textbook legal architecture, how do they perform against the actual heuristics of master practitioners?
          </p>
          
          <p>
            To answer this, Baseline Research moved beyond synthetic testing. For our next-generation dataset (HRE v2), we ingested over 15,000 pages of raw, unedited transcripts from three world-class Talmudic scholars, representing the highest echelons of both American and Israeli academies.
          </p>

          <p>
            We did not ask them to write test questions. We algorithmically extracted the exact logical mechanics they employ while teaching complex Halacha—instances where they explain why a structural rule overrides a statistical probability, or how a common translation trap is overturned by a precise legal distinction.
          </p>

          <p>
            By extracting these mechanics directly from the oral transmission of master scholars, we have converted thousands of hours of elite human reasoning into a machine-readable, certified evaluation dataset. It is fundamentally impossible for a model to "guess" its way through this architecture.
          </p>
        </section>

        <section className="wp-section">
          <h2>Why This Matters</h2>
          <p>
            Words are not transparent containers, and numbers are not automatically authoritative. When a language model encounters a statistical majority, its probability training overrides explicit structural constraints.
          </p>

          <p>
            In a religious context, this produces bad theology. In a legal, medical, or compliance context, this failure mode is actively dangerous. A model that cannot suppress a statistical likelihood to obey a formal structural rule cannot be trusted in high-stakes reasoning environments.
          </p>

          <p>
            AI Labs are currently convening "Faith-AI Roundtables" to solve religious bias and handle religious queries. But currently, they evaluate religious queries merely for "offensiveness" or "safety." They ask if the model is polite. They do not evaluate if the model possesses structural logical integrity.
          </p>

          <p className="wp-emphasis">
            A model can be perfectly polite and structurally broken.
          </p>

          <p>
            Baseline Research provides the evaluation harness to measure that difference. We do not sell comfort, and we are not a theological review board. We build the empirical datasets and evaluation architecture that prove whether a model is actually reasoning, or just doing math in disguise.
          </p>
        </section>
      </div>
    </div>
  );
};

export default Whitepaper;
