import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'C++',
    Svg: require('@site/static/img/cpp.svg').default,
    description: (
      <>
        The object-oriented nature of C++ enhances code organization and reusability
        in embedded projects, facilitating easier maintenance and scalability
      </>
    ),
  },
  {
    title: 'SystemRDL',
    Svg: require('@site/static/img/accellera.svg').default,
    description: (
      <>
        Accellera SystemRDL is a standardized language
        used for describing register maps and memory-mapped structures in hardware designs,
        facilitating efficient communication between software and hardware components.
      </>
    ),
  },
  {
    title: 'PeakRDL',
    Svg: require('@site/static/img/peakrdl.svg').default,
    description: (
      <>
        PeakRDL is an open-source, Python-based toolchain that implements
        the SystemRDL 2.0 standard for efficient register map description
        and generation in hardware designs
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
