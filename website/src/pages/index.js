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
    title: <>Pipelining Web Pages For High Performance</>,
    imageUrl: 'img/undraw_fast_loading_0lbh.svg',
    description: (
      <>
        Stream content and resources using a single/initial HTTP connection made to fetch HTML page.
      </>
    ),
  },
  {
    title: <>No Setup Required</>,
    imageUrl: 'img/undraw_online_media_62jb.svg',
    description: (
      <>
        There is no need for compiling, preparing, optimizing, uglifying source files
        All is done automatically by response configuration.
      </>
    ),
  },
  {
    title: <>Fast Websites With No Effort</>,
    imageUrl: 'img/undraw_dev_productivity_umsq.svg',
    description: (
      <>
        Bigpipe Response is analyzing and building exactly what needed and send it back to the browser.
        this includes `HTML, JavaScript, JavaScript Server Side Rendering, SASS, i18n. and more`
      </>
    ),
  },
  {
    title: <>Plug-able Architecture</>,
    imageUrl: 'img/undraw_apps_m7mh.svg',
    description: (
      <>
        Use any Javascript framework and more. by creating a custom processor you can easily pipe any source file.
        [React](https://reactjs.org/) is supported out of the box.
      </>
    ),
  },
  {
    title: <>Packing Made Easy</>,
    imageUrl: 'img/undraw_abstract_x68e.svg',
    description: (
      <>
        You can config what resource to load, how to bundle it and how to embed it by telling the response object exactly what you need.
      </>
    ),
  },
  {
    title: <>i18n Optimization</>,
    imageUrl: 'img/undraw_around_the_world_v9nu.svg',
    description: (
      <>
        django built-in internalization is used and extends to be supported by javascript components and server-side rendering.
      </>
    ),
  }
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
      description="Description will go into a meta tag in <head />">
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
