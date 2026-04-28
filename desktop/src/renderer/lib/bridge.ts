type DesktopBridge = Window['pixllmDesktop'];

function desktopBridge(): DesktopBridge {
  const bridge = window.pixllmDesktop as DesktopBridge | undefined;
  if (!bridge) {
    throw new Error('Desktop bridge is not available. Restart the app.');
  }
  return bridge;
}

function requireMethod<T extends keyof DesktopBridge>(name: T): DesktopBridge[T] {
  const bridge = desktopBridge();
  const fn = bridge[name];
  if (typeof fn !== 'function') {
    throw new Error(`Desktop bridge method '${String(name)}' is missing. Fully restart the app.`);
  }
  return fn as DesktopBridge[T];
}

function toError(error: unknown): Error {
  return error instanceof Error ? error : new Error(String(error));
}

export async function invokeDesktop<T>(name: keyof DesktopBridge, ...args: unknown[]): Promise<T> {
  try {
    return await (requireMethod(name) as (...callArgs: unknown[]) => Promise<T>)(...args);
  } catch (error) {
    throw toError(error);
  }
}

export function subscribeDesktopEvent<T>(
  name: keyof DesktopBridge,
  callback: (payload: T) => void
): () => void {
  const subscribe = requireMethod(name) as (cb: (payload: T) => void) => () => void;
  return subscribe(callback);
}

export const desktop = new Proxy({} as DesktopBridge, {
  get: (_target, name) => (...args: unknown[]) => invokeDesktop(name as keyof DesktopBridge, ...args)
}) as DesktopBridge;
