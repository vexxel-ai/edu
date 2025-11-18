%-------------------------
% Resume in Latex
% Author
% License : MIT
%------------------------

%---- Required Packages and Functions ----

\documentclass[a4paper,11pt]{article}
\usepackage{latexsym}
\usepackage{xcolor}
\usepackage{float}
\usepackage{ragged2e}
\usepackage[empty]{fullpage}
\usepackage{wrapfig}
\usepackage{lipsum}
\usepackage{tabularx}
\usepackage{titlesec}
\usepackage{geometry}
\usepackage{marvosym}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage{fontawesome5}
\usepackage{multicol}
\usepackage{graphicx}
\usepackage{cfr-lm}
\usepackage[T1]{fontenc}
\setlength{\multicolsep}{0pt} 
\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\geometry{left=1.4cm, top=0.8cm, right=1.2cm, bottom=1cm}
% Adjust margins
%\addtolength{\oddsidemargin}{-0.5in}
%\addtolength{\evensidemargin}{-0.5in}
%\addtolength{\textwidth}{1in}
\usepackage[most]{tcolorbox}
\tcbset{
	frame code={}
	center title,
	left=0pt,
	right=0pt,
	top=0pt,
	bottom=0pt,
	colback=gray!20,
	colframe=white,
	width=\dimexpr\textwidth\relax,
	enlarge left by=-2mm,
	boxsep=4pt,
	arc=0pt,outer arc=0pt,
}

\urlstyle{same}

\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-7pt}]

%-------------------------
% Custom commands
\newcommand{\resumeItem}[2]{
  \item{
    \textbf{#1}{\hspace{0.5mm}#2 \vspace{-0.5mm}}
  }
}

\newcommand{\resumePOR}[3]{
\vspace{0.5mm}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
        \textbf{#1}\hspace{0.3mm}#2 & \textit{\small{#3}} 
    \end{tabular*}
    \vspace{-2mm}
}

\newcommand{\resumeSubheading}[4]{
\vspace{0.5mm}\item
    \begin{tabular*}{0.98\textwidth}[t]{l@{\extracolsep{\fill}}r}
        \textbf{#1} & \textit{\footnotesize{#4}} \\
        \textit{\footnotesize{#3}} &  \footnotesize{#2}\\
    \end{tabular*}
    \vspace{-2.4mm}
}

\newcommand{\resumeProject}[4]{
\vspace{0.5mm}\item
    \begin{tabular*}{0.98\textwidth}[t]{l@{\extracolsep{\fill}}r}
        \textbf{#1} & \textit{\footnotesize{#3}} \\
        \footnotesize{\textit{#2}} & \footnotesize{#4}
    \end{tabular*}
    \vspace{-2.4mm}
}

\newcommand{\resumeSubItem}[2]{\resumeItem{#1}{#2}\vspace{-4pt}}
\renewcommand{\labelitemii}{$\bullet$}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*,labelsep=1mm,label=]}
\newcommand{\resumeHeadingSkillStart}{\begin{itemize}[leftmargin=*,itemsep=1.7mm, rightmargin=2ex, label=]}
\newcommand{\resumeItemListStart}{\begin{justify}\begin{itemize}[leftmargin=3ex, rightmargin=2ex, noitemsep,labelsep=1.2mm,itemsep=0mm]\small}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}\vspace{2mm}}
\newcommand{\resumeHeadingSkillEnd}{\end{itemize}\vspace{-2mm}}
\newcommand{\resumeItemListEnd}{\end{itemize}\end{justify}\vspace{-2mm}}
\newcommand{\cvsection}[1]{%
\vspace{2mm}
\begin{tcolorbox}
    \textbf{\large #1}
\end{tcolorbox}
    \vspace{-4mm}
}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}%
\newcolumntype{R}{>{\raggedleft\arraybackslash}X}%
\newcolumntype{C}{>{\centering\arraybackslash}X}%
%---- End of Packages and Functions ------

%-------------------------------------------
%%%%%%  CV STARTS HERE  %%%%%%%%%%%
%%%%%% DEFINE ELEMENTS HERE %%%%%%%
\newcommand{\name}{Igor Lima Rocha Azevedo} % Your Name
\newcommand{\course}{Master Research Artificial Intelligence and Machine Learning} % Your Program
\newcommand{\roll}{02487347} % Your Roll No.
\newcommand{\phone}{+44 07782 793183} % Your Phone Number
\newcommand{\emailaa}{i.lima-rocha-azevedo25@imperial.ac.uk} %Email 2
\newcommand{\website}{igorazevedo.com} % Your Website

\begin{document}
\fontfamily{cmr}\selectfont

%----------HEADING-----------------
{
\centering % Center the header block
\textbf{\Large \name} \\ % Name on its own line
\vspace{1.5mm} % Optional: add a little space
{\footnotesize % Make all contact info smaller
\href{mailto:\emailaa}{\faEnvelope\ \emailaa} \quad|\quad % Email
\href{https://\website}{\faGlobe\ \website} \quad|\quad % Website
\href{https://github.com/igor17400}{\faGithub\ GitHub} \quad|\quad % GitHub
\href{https://www.linkedin.com/in/igorlrazevedo/}{\faLinkedin\ LinkedIn} \quad|\quad  % LinkedIn
\faPhone\ \phone % Phone
}
\par % End the centered paragraph
}

%-----------EDUCATION-----------
\section{\textbf{Education}}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Imperial College London}{}
      {Master of Research (MRes) in Artificial Intelligence and Machine Learning}{London, UK | Sep 2025 - Exp. Sep 2026}
      \vspace{-1.0mm}
      \resumeItemListStart
        \item{Conducting research on generative and contrastive deep learning for predicting rare events. Supervised by Prof. Pedro Mediano}
      \resumeItemListEnd
      \vspace{-2.0mm}
    \resumeSubheading
      {University of Brasilia}{GPA: 4.35 / 5.0}
      {Electrical Engineering}{Brasilia, Brazil | Aug 2016 - Jun 2022}
      \vspace{-1.0mm}
      \resumeItemListStart
        \item{Conducted research on FPGAs, as well as Machine Learning for audio codec optimization and financial markets. Supervised by Prof. Edson Mintsu Hung.}
      \resumeItemListEnd
    \vspace{-3.0mm}
  \resumeSubHeadingListEnd
\vspace{-5.5mm}

%-----------RESEARCH EXPERIENCE-----------------
\section{\textbf{Research Experience}}
\resumeSubHeadingListStart

    \resumeProject
        {Research Scholar at The University of Tokyo}
        {\textit{[Fill in hrs/week, e.g., Full-time (40 hrs/week)]}}
        {Tokyo, Japan | \textit{Apr 2023 – Apr 2025}}{}
        \vspace{-5.0mm}
        \resumeItemListStart
            \item{Contributed to deep learning research projects supervised by Prof. Toyotaro Suzumura and Dr. Yuichiro Yasui.}
            \item{Collaborated with Nikkei Inc. (a Financial Times group company) to design novel recommender system models.}
            \item{Developed deep learning models for high-frequency stock price forecasting.}
            \item{Researched foundational LLMs, exploring retrieval-augmented generation (RAG) and long-context handling.}
        \resumeItemListEnd
        \vspace{-2mm}

    \resumeProject
        {Research Intern at Cellcrypt: Quantum-Safe Encrypted Calls}
        {\textit{[Fill in hrs/week, e.g., Part-time (20 hrs/week)]}}
        {London, UK (Remote) | \textit{Sep 2020 – Jun 2021}}{}
        \vspace{-5.0mm}
        \resumeItemListStart
            \item{Optimized machine learning models to improve VoIP performance by enhancing call quality and reducing latency.}
            \item{Built an ML pipeline for automated PJSIP (multimedia communication library written in C with high level API in C++) parameter tuning, which boosted call quality metrics by 7\%.}
        \resumeItemListEnd
        \vspace{-2mm}
\resumeSubHeadingListEnd
\vspace{-5.5mm}

\section{\textbf{Professional Experience}}
\resumeSubHeadingListStart
    \resumeProject
        {Developer \& Development Team Lead at VOGA}
        {\textit{[Fill in hrs/week, e.g., Full-time (40 hrs/week)]}}
        {\textit{Brasilia, Brazil | Jul 2021 – Apr 2023}}{}
        \vspace{-5.0mm}
        \resumeItemListStart
            \item{Started as a Developer, later promoted to Development Team Lead.}
            \item{Led system integration for VOGA post-acquisition by BTG Pactual, South America’s largest investment bank.}
            \item{Architected and developed a centralized platform to monitor and track over USD 300 million in managed assets.}
            \item{Transitioned from full-stack (Flask/NextJS) to DevOps, managing AWS infrastructure (EC2, ECS, RDS, VPC, S3) with Terraform, automating CI/CD with Jenkins, and securing with Cloudflare.}
        \resumeItemListEnd
        \vspace{-2mm}
\resumeSubHeadingListEnd
\vspace{-5.5mm}

%-----------PUBLICATIONS-----------------
\section{\textbf{Selected Publications}}
  \resumeSubHeadingListStart
    % Tip: Add all authors. Bolding your name is standard practice.
    \resumeSubheading
        {[\textit{Authors TBD e.g., Y. Yasui, T. Suzumura,} \textbf{I. L. R. Azevedo}]. "A Look Into News Avoidance Through AWRS: An Avoidance-Aware Recommender System"}
        {\textit{Jul 2024}}
        {Submitted to SIAM International Conference on Data Mining (SDM'25)}
        {}
        \vspace{-1.0mm}
        \resumeItemListStart
            \item{A novel architecture for learning from and modeling user avoidance patterns in recommendations.}
            \item{Achieves better performance on key metrics across multilingual datasets in Japanese, English, and Nowergian.}
        \resumeItemListEnd
    \vspace{-1.5mm}

    \resumeSubheading
        {[\textit{Authors TBD,} \textbf{I. L. R. Azevedo}]. "NewsReX: A More Efficient Approach to News Recommendation with Keras 3 and JAX"}
        {\textit{Aug 2025}}
        {Under Review}
        {}
        \vspace{-1.0mm}
        \resumeItemListStart
            \item{An open-source JAX-based library for reproducible state of the art news recommendation models.}
            \item{Achieved up to 41\% faster model training for consumer-grade GPUs.}
        \resumeItemListEnd
    \vspace{-1.5mm}

    \resumeSubheading
        {[\textit{Authors TBD,} \textbf{I. L. R. Azevedo}]. "A SHA-3 Co-Processor for IoT Applications"}
        {\textit{Nov 2020}}
        {IEEE Workshop on Communication Networks and Power Systems (WCNPS'20)}
        {}
        \vspace{-1.0mm}
        \resumeItemListStart
            \item{Implements a SHA-3 Co-Processor in FPGA using C++ suitable for IoT applications.}
            \item{Proposes solution is about 65\% faster than the ARM Cortex-A9 when oputing SHA-3.}
        \resumeItemListEnd
    \vspace{-1.5mm}

  \resumeSubHeadingListEnd
\vspace{-5.5mm}

%-----------AWARDS-----------------
\section{\textbf{Awards}}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Society for Industrial and Applied Mathematics (SIAM) Travel Award}
      {}
      {}
      {May 2025}
      \vspace{-5.0mm}
      \resumeItemListStart
        \item{Recognizing promising early-career researchers in the field of data mining.}
      \resumeItemListEnd
      \vspace{-3.5mm}

    \resumeSubheading
      {Japanese Government Research Scholarship (MEXT)}
      {}
      {}
      {April 2023 – April 2025}
      \vspace{-5.0mm}
      \resumeItemListStart
        \item{A prestigious and highly competitive scholarship to support students conducting research at higher education institutions in Japan.}
      \resumeItemListEnd
      \vspace{-3.5mm}

    \resumeSubheading
      {Brazilian Government Scientific Initiation Scholarship (PIBIC)}
      {}
      {}
      {August 2019 – July 2020}
      \vspace{-5.0mm}
      \resumeItemListStart
        \item{A federal government-funded program to support undergraduate students engaging in research and innovation.}
      \resumeItemListEnd
      \vspace{-3.5mm}

  \resumeSubHeadingListEnd
\vspace{-5.5mm}

%-----------OPEN SOURCE CONTRIBUTIONS-----------------
\section{\textbf{Open Source Contributions}}
   \resumeSubHeadingListStart
      \resumeSubheading
        {Newsreclib}
        {\href{https://github.com/andreeaiana/newsreclib/pull/12}{\textit{\underline{Pull Request}}}}
        {SOTA Model Implementation}
        {\textit{May 2024}}
        \vspace{-1.0mm}
        \resumeItemListStart
         \item{Contributed a state-of-the-art model implementation (PP-REC) to the main news recommendation framework.}
        \resumeItemListEnd
        \vspace{-3.5mm}

      \resumeSubheading
        {Microsoft Qlib}
        {\href{https://github.com/microsoft/qlib/pull/990}{\textit{\underline{Pull Request}}}}
        {Data Support Expansion}
        {\textit{Apr 2022}}
        \vspace{-1.0mm}
        \resumeItemListStart
         \item{Added data support for the Brazilian stock market (B3), enabling local researchers to use Qlib's ML models.}
        \resumeItemListEnd
        \vspace{-3.5mm}
    \resumeSubHeadingListEnd
\vspace{-5.5mm}

%-----------PROFESSIONAL & OUTREACH ACTIVITIES-----------------
\section{\textbf{Professional \& Outreach Activities}}
   \resumeSubHeadingListStart
     \resumeSubheading
       {Commercial Director}
       {\textit{[Fill in hrs/week, e.g., Part-time (15 hrs/week)]}}
       {Electrical Engineering Junior Enterprise (\href{https://enetec.net.br//}{\textit{\underline{ENETEC}}})}
       {Brasilia, Brazil | June 2019 – April 2020}
       \resumeItemListStart
         \item{Led the team to achieve annual goals set by the \href{https://brasiljunior.org.br/}{\textit{\underline{National Association of Junior Enterprises in Brazil}}}, securing projects worth approximately USD 30,000, which funded training and development for company members.}
       \resumeItemListEnd
   \resumeSubHeadingListEnd
\vspace{-5.5mm}

%-----------TECHNICAL SKILLS-----------------
\section{\textbf{Technical Skills}}
  \resumeSubHeadingListStart
    \item{\textbf{Languages:} Portuguese (Native), English (Fluent), Spanish (Intermediate), Japanese (Beginner)}
    \item{\textbf{Programming & Machine Learning:}
      \resumeItemListStart
        \item{\textbf{Python (Advanced):} Extensive experience using \textbf{PyTorch}, \textbf{TensorFlow}, \textbf{Keras}, \textbf{JAX}, and \textbf{SciKit-Learn} to build and optimize deep learning models for recommender systems, LLMs, and VoIP performance (at Univ. of Tokyo, Cellcrypt).}
        \item{\textbf{AI Frameworks:} Researched and applied \textbf{Lightning AI}, \textbf{CrewAI}, and \textbf{DSPy} for LLM and quantitative finance model development.}
      \resumeItemListEnd
    }
    \item{\textbf{DevOps & Full-Stack:}
      \resumeItemListStart
        \item{\textbf{DevOps & Cloud:} Architected and managed \textbf{AWS} infrastructure (\textbf{EC2, ECS, RDS, VPC, S3}) using \textbf{Terraform}; built CI/CD pipelines with \textbf{Jenkins} (at VOGA).}
        \item{\textbf{Web & Other:} Full-stack development with \textbf{Flask} and NextJS; proficiency in \textbf{SQL}, \textbf{C/C++} (for PJSIP, FPGAs), \textbf{Java}, \textbf{MATLAB}, and \textbf{Linux}.}
      \resumeItemListEnd
    }
  \resumeSubHeadingListEnd
\vspace{-5.5mm}

%-------------------------------------------
\end{document}