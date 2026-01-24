import { motion } from "framer-motion";

import { SummarizeIcon } from "./icons";

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-2xl">
        <p className="flex flex-row justify-center gap-4 items-center">
          <SummarizeIcon size={32} />
        </p>
        <div className="text-foreground">
          <p>
            <b>Resummate</b> is an AI career strategist that transforms your resume into a &quot;Top 1%&quot; application.
          </p>
          <p className="mt-4">
            Resummate provides interactive coaching and detailed feedback based on modern hiring standards and ATS optimization.
            Get personalized suggestions for improving your resume, from action verbs to keyword alignment for your target role.
          </p>
          <p className="mt-4">
            Start by uploading your resume to receive expert feedback.
          </p>
        </div>
      </div>
    </motion.div>
  );
};
