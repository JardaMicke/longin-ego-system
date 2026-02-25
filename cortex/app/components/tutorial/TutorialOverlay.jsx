import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const steps = [
  {
    target: '.status-indicator',
    title: 'System Status',
    content: 'Tento indikátor zobrazuje aktuální stav systému LONGIN EGO. Zelená pulzující tečka značí, že systém je plně operační a připraven.',
    position: 'bottom-left'
  },
  {
    target: '.sidebar.left',
    title: 'Module Selection',
    content: 'Zde přepínáte mezi hlavními moduly. "Core Chat" pro interakci, "3D Monitor" pro vizualizaci, a další nástroje pro správu systému.',
    position: 'right'
  },
  {
    target: '.metrics-panel',
    title: 'Live Telemetry',
    content: 'Reálná data ze senzorů systému. Sledujte vytížení CPU, RAM a teplotu GPU (kritické pro Single-GPU-Lock).',
    position: 'right'
  },
  {
    target: '.module-panel',
    title: 'Main Workspace',
    content: 'Hlavní pracovní plocha. Zde probíhá komunikace s Egem, vizualizace dat nebo správa úloh podle vybraného modulu.',
    position: 'left' // nebo bottom
  },
  {
    target: '.sidebar.right',
    title: 'Control Plane',
    content: 'Ovládací panel a Context Stack. Zde vidíte aktivní kontext, historii operací a rychlé příkazy.',
    position: 'left'
  }
];

export const TutorialOverlay = ({ onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState(null);

  useEffect(() => {
    const updateTarget = () => {
      const target = document.querySelector(steps[currentStep].target);
      if (target) {
        const rect = target.getBoundingClientRect();
        setTargetRect({
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height,
          bottom: rect.bottom,
          right: rect.right
        });
      }
    };

    updateTarget();
    window.addEventListener('resize', updateTarget);
    return () => window.removeEventListener('resize', updateTarget);
  }, [currentStep]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (!targetRect) return null;

  const step = steps[currentStep];

  // Calculate tooltip position
  let tooltipStyle = {};
  if (step.position === 'right') {
    tooltipStyle = { top: targetRect.top, left: targetRect.right + 20 };
  } else if (step.position === 'left') {
    tooltipStyle = { top: targetRect.top, right: window.innerWidth - targetRect.left + 20 };
  } else if (step.position === 'bottom-left') {
    tooltipStyle = { top: targetRect.bottom + 20, left: targetRect.left };
  } else {
    tooltipStyle = { top: targetRect.bottom + 20, left: targetRect.left };
  }

  return (
    <AnimatePresence>
      <div className="tutorial-overlay" style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        pointerEvents: 'none' // Allow clicking through if needed, but we usually want to block
      }}>
        {/* Dimmed Background with Hole */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          clipPath: `polygon(
            0% 0%, 
            0% 100%, 
            100% 100%, 
            100% 0%, 
            ${targetRect.left}px 0%, 
            ${targetRect.left}px ${targetRect.top}px, 
            ${targetRect.right}px ${targetRect.top}px, 
            ${targetRect.right}px ${targetRect.bottom}px, 
            ${targetRect.left}px ${targetRect.bottom}px, 
            ${targetRect.left}px 0%
          )`
        }} />

        {/* Highlight Border */}
        <motion.div
          layoutId="highlight"
          initial={false}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          style={{
            position: 'absolute',
            top: targetRect.top - 4,
            left: targetRect.left - 4,
            width: targetRect.width + 8,
            height: targetRect.height + 8,
            border: '2px solid var(--accent)',
            borderRadius: '8px',
            boxShadow: '0 0 20px var(--accent)',
            pointerEvents: 'none'
          }}
        />

        {/* Tooltip Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          key={currentStep}
          style={{
            position: 'absolute',
            ...tooltipStyle,
            pointerEvents: 'auto',
            width: '300px',
            background: 'var(--panel)',
            border: '1px solid var(--accent)',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
          }}
        >
          <div style={{ 
            fontFamily: 'var(--font-orbitron)', 
            color: 'var(--accent)', 
            marginBottom: '10px',
            fontSize: '14px',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            {step.title} <span style={{opacity: 0.5, fontSize: '10px', float: 'right'}}>{currentStep + 1} / {steps.length}</span>
          </div>
          <div style={{ 
            fontSize: '13px', 
            color: 'var(--text)', 
            lineHeight: '1.5',
            marginBottom: '20px' 
          }}>
            {step.content}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button 
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-dim)',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Skip
            </button>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={handlePrev}
                disabled={currentStep === 0}
                style={{
                  background: 'transparent',
                  border: '1px solid var(--border)',
                  color: currentStep === 0 ? 'var(--text-dim)' : 'var(--text)',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  cursor: currentStep === 0 ? 'default' : 'pointer',
                  opacity: currentStep === 0 ? 0.5 : 1
                }}
              >
                Back
              </button>
              <button 
                onClick={handleNext}
                style={{
                  background: 'var(--accent)',
                  border: 'none',
                  color: '#000',
                  padding: '6px 16px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '12px'
                }}
              >
                {currentStep === steps.length - 1 ? 'Finish' : 'Next'}
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
