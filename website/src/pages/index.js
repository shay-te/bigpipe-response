/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from 'react';
import classnames from 'classnames';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';

const features = [
  {
    title: <>No More Bundling</>,
    imageUrl: 'img/undraw_fast_loading_0lbh.svg',
    description: (
      <>
Bigpipe Response bundle code automatically with minimum file size.
<br></br><br></br>
Bundled code is transformed using the build in <a>processors</a> (supoport React/SCSS out of the box).
      </>
    ),
  },
  {
    title: <>Optimization Of Performance Cost Time</>,
    imageUrl: 'img/undraw_dev_productivity_umsq.svg',
    description: (
      <>
Bigpipe Response Bundle, Optimize And Render almost anything into the screen
<br></br><br></br>
It frees more time to focus on the development of the application.

      </>
    ),
  },
  {
    title: <>It Doesnt Override Anything</>,
    imageUrl: 'img/undraw_online_media_62jb.svg',
    description: (
      <>
Bigpipe Response will find your code without changing the existing project structure.
<br></br><br></br>
It's another tool in the belt, A response Object the do more.
      </>
    ),
  },
  {
    title: <>Expend capabilities with minimum effort</>,
    imageUrl: 'img/undraw_abstract_x68e.svg',
    description: (
      <>
Bigpipe Response is plug-able and can process almost anything
<br></br><br></br>
Custom Processors are created by `configuration` `YAML` files And `code`.
      </>
    ),
  },
];

function Feature({imageUrl, title, description}) {
  const imgUrl = useBaseUrl(imageUrl);
  return (
    <div className={classnames('col col--4', styles.feature)}>
      {imgUrl && (
        <div className="text--center">
          <img className={styles.featureImage} src={imgUrl} alt={title} />
        </div>
      )}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Bigpipe Response <head />">
      <header className={classnames('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div className={styles.buttons}>
            <Link
              className={classnames(
                'button button--outline button--secondary button--lg',
                styles.getStarted,
              )}
              to={useBaseUrl('docs/main')}>
              Get Started
            </Link>

            <span className={styles['index-ctas-github-button']}>
              <iframe
                src="https://ghbtns.com/github-btn.html?user=shacoshe&amp;repo=bigpipe-response&amp;type=star&amp;count=false&amp;size=large"
                frameBorder={0}
                scrolling={0}
                width={160}
                height={30}
                style={{marginLeft: '10px', marginTop: '5px'}}
                title="GitHub Stars"
              />
            </span>

          </div>
        </div>
      </header>
      <main>
        {features && features.length && (
          <section className={styles.features}>
            <div className="container">
              <div className="row">
                {features.map((props, idx) => (
                  <Feature key={idx} {...props} />
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
    </Layout>
  );
}

export default Home;
